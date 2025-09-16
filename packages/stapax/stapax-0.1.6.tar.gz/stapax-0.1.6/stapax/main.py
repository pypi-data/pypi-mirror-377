import logging
import os
import uuid
from pathlib import Path
import wadler_lindig as wld

import hydra
import jax
import torch
from hydra.types import RunMode
from omegaconf import DictConfig
from pytorch_lightning import Trainer
from pytorch_lightning.profilers import SimpleProfiler

from stapax.callbacks.save_test_output import CollectTestOutputsCallback
from stapax.config import load_typed_root_config
from stapax.dataset import get_dataloaders
from stapax.logging import get_lightning_logger, setup_logging
from stapax.loss.get_loss_fns import get_loss_fns
from stapax.metric import get_metrics_for_heads
from stapax.misc.early_stopping import EarlyStoppingWithWarmup
from stapax.misc.load_model import load_model
from stapax.misc.save_checkpoint import CheckpointManager
from stapax.misc.step_tracker import StepTracker
from stapax.model_wrapper import JaxLightningWrapper
from stapax.models import get_model


def main(cfg_dict: DictConfig) -> float | None:
    cfg = load_typed_root_config(cfg_dict)
    setup_logging(level=cfg.log_level)
    logger = logging.getLogger(__name__)

    torch.manual_seed(cfg.seed)
    is_multirun = hydra.core.hydra_config.HydraConfig.get()["mode"] == RunMode.MULTIRUN

    logger.info(f"is_multirun: {is_multirun}")
    logger.info(jax.devices())

    if cfg.output_dir is None:
        # Set up the output directory.
        while os.path.exists(
            output_dir := (
                Path(hydra.core.hydra_config.HydraConfig.get()["runtime"]["output_dir"])
                / str(uuid.uuid4())[:4]
            )
        ):
            pass
        output_dir = output_dir
    else:
        hydra_out = str(
            hydra.core.hydra_config.HydraConfig.get()["runtime"]["output_dir"]
        ).split("outputs")
        output_dir = Path(cfg.output_dir) / Path("outputs" + hydra_out[1])

    os.makedirs(output_dir, exist_ok=True)

    cfg.output_dir = output_dir
    lightning_logger = get_lightning_logger(
        cfg=cfg, output_dir=output_dir, is_multirun=is_multirun
    )

    # For keeping track of global number of steps
    step_tracker = StepTracker()

    if cfg.use_compilation_cache:
        os.makedirs(".cache/jax_cache", exist_ok=True)
        jax.config.update("jax_compilation_cache_dir", ".cache/jax_cache")
        jax.config.update(
            "jax_persistent_cache_min_entry_size_bytes", int(1e10)
        )  # 10GB
        jax.config.update("jax_persistent_cache_min_compile_time_secs", 1.0)
        jax.config.update(
            "jax_persistent_cache_enable_xla_caches",
            "xla_gpu_per_fusion_autotune_cache_dir",
        )

    key = jax.random.PRNGKey(cfg.seed)
    key, data_key = jax.random.split(key, 2)
    train_dataloader, val_dataloader, test_dataloader = get_dataloaders(
        cfg=cfg.dataset,
        batch_size_train_val=cfg.train.batch_size,
        batch_size_test=cfg.test.batch_size,
        key=data_key,
        step_tracker=step_tracker,
        logger=lightning_logger,
    )

    key, pl_key, model_key = jax.random.split(key, 3)
    model, model_state, filter_spec, param_count = get_model(
        cfg=cfg.model,
        input_feature_dim=train_dataloader.input_feature_dim,
        input_dtype=train_dataloader.dtype,
        target_feature_dim=train_dataloader.target_feature_dim,
        key=model_key,
        timesteps=train_dataloader.input_timesteps,
        num_embeddings=train_dataloader.num_embeddings,
    )
    # add param count to wandb config
    lightning_logger.experiment.config.update({"param_count": param_count})

    if cfg.load_from_checkpoint is not None:
        model, model_state = load_model(model, model_state, cfg.load_from_checkpoint)

    pl_model = JaxLightningWrapper(
        model=model,
        model_state=model_state,
        model_filter_spec=filter_spec,
        test_config=cfg.test,
        train_config=cfg.train,
        loss_fns=get_loss_fns(*cfg.model.heads),
        step_tracker=step_tracker,
        key=pl_key,
    )

    callbacks = []
    callbacks += train_dataloader.callbacks or []

    # add callback to save test outputs
    callbacks.append(CollectTestOutputsCallback(save_dir=output_dir))

    # Set up checkpointing.
    checkpoints = CheckpointManager(
        output_dir=output_dir,
        cfg=cfg.train.checkpoint,
        step_tracker=step_tracker,
    )
    callbacks.append(checkpoints)

    if cfg.train.early_stopping is not None:
        callbacks.append(
            EarlyStoppingWithWarmup(
                monitor=cfg.train.early_stopping.metric,
                min_delta=cfg.train.early_stopping.min_delta,
                patience=cfg.train.early_stopping.patience,
                verbose=cfg.train.early_stopping.verbose,
                mode=cfg.train.early_stopping.mode,
                warmup_steps=cfg.train.early_stopping.warmup_steps,
            )
        )

    # Profiler
    profiler = SimpleProfiler(dirpath=output_dir / "profiler", filename="profiler")

    callbacks += get_metrics_for_heads(model)

    steps_per_epoch = len(train_dataloader)

    if (
        cfg.train.check_val_every_n_epoch is not None
        and cfg.train.val_check_interval > steps_per_epoch
    ):
        logger.info(f"Clamping validation frequency to {steps_per_epoch}")
        cfg.train.val_check_interval = steps_per_epoch

    trainer = Trainer(
        max_steps=cfg.train.max_steps or -1,
        max_epochs=cfg.train.max_epochs,
        min_steps=cfg.train.min_steps,
        min_epochs=cfg.train.min_epochs,
        logger=lightning_logger,
        val_check_interval=min(cfg.train.val_check_interval, steps_per_epoch),
        check_val_every_n_epoch=cfg.train.check_val_every_n_epoch,
        callbacks=callbacks,
        enable_model_summary=False,  # model summary does not work with jax
        profiler=profiler,
        log_every_n_steps=min(cfg.train.log_every_n_steps, steps_per_epoch),
    )

    logger.info(f"Config: {wld.pformat(cfg)}")

    best_val_metric = None
    if cfg.mode == "train" or cfg.mode == "all":
        trainer.fit(
            pl_model,
            train_dataloader,
            val_dataloader,
        )

        try:
            # the MAD benchmark does its sweep on the test accuracy (because the test data deviates from the validation data). It furthermore just uses the last model for evaluation.
            if not cfg.sweep_on_test:
                # load best checkpoint for testing
                model_path, state_path, best_val_metric = (
                    checkpoints.get_best_checkpoint()
                )
                pl_model.model, pl_model.model_state = load_model(
                    pl_model.model, pl_model.model_state, model_path
                )
        except Exception as e:
            logger.error(
                f"Error loading best checkpoint, Keeping most recent model loaded: {e}"
            )

    if cfg.mode == "test" or cfg.mode == "all":
        test_results = trainer.test(pl_model, test_dataloader)

    # Finish wandb experiment manually (required for doing multiruns)
    lightning_logger.experiment.finish()

    # We need to return the best metric here for the hyperparameter optimization
    if not cfg.sweep_on_test:
        return best_val_metric
    # The MAD benchmark should use the test accuracy
    else:
        return test_results[0]["test/multiclass/masked_accuracy"]


if __name__ == "__main__":
    main()
