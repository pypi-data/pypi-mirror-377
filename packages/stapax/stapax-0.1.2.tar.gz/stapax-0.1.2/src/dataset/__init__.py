import logging
import jax.random as jr
from jaxtyping import PRNGKeyArray
from pytorch_lightning.loggers import Logger

from src.misc.step_tracker import StepTracker

from .types import CustomDataloader, Stage
from .util import numpy_collate
from src.dataset.store import get_dataset_cfgs_type, RegisteredDatasets

from src.misc.stores import import_all_siblings

logger = logging.getLogger(__name__)


import_all_siblings(__name__, __file__)
DatasetConfig = get_dataset_cfgs_type()


def get_dataloader(
    cfg: DatasetConfig,
    batch_size: int,
    stage: Stage,
    key: PRNGKeyArray,
    step_tracker: StepTracker | None,
    logger: Logger | None = None,
) -> CustomDataloader:
    try:
        dataset = RegisteredDatasets[cfg.name][0](
            cfg=cfg, stage=stage, step_tracker=step_tracker, key=key
        )
    except KeyError:
        logger.error(f"Dataset {cfg.name} not found")
        raise ValueError(f"Dataset {cfg.name} not found")

    dataloader = CustomDataloader(
        dataset=dataset,
        batch_size=batch_size,
        shuffle=cfg.shuffle if stage == "train" else False,
        collate_fn=numpy_collate,
        input_feature_dim=dataset.input_feature_dim,
        target_feature_dim=dataset.target_feature_dim,
        input_timesteps=dataset.input_timesteps,
        dtype=dataset.dtype,
        callbacks=dataset.callbacks,
        logger=logger,
        num_embeddings=dataset.num_embeddings,
        num_workers=cfg.num_workers,
        # multiprocessing_context="spawn",  # needed for jax to work properly with multiple dataloaders
        # persistent_workers=True,
        multiprocessing_context="spawn"
        if cfg.num_workers > 0
        else None,  # needed for jax to work properly with multiple dataloaders
        persistent_workers=cfg.num_workers
        > 0,  # Only use persistent workers when num_workers > 0
    )
    return dataloader


def get_dataloaders(
    cfg: DatasetConfig,
    batch_size_train_val: int,
    batch_size_test: int | None,
    key: PRNGKeyArray,
    step_tracker: StepTracker | None,
    logger: Logger | None = None,
) -> tuple[CustomDataloader, CustomDataloader, CustomDataloader]:
    key, train_key, val_key, test_key = jr.split(key, 4)
    train_dataloader = get_dataloader(
        cfg,
        batch_size=batch_size_train_val,
        stage="train",
        key=train_key,
        step_tracker=step_tracker,
        logger=logger,
    )
    val_dataloader = get_dataloader(
        cfg,
        batch_size=batch_size_train_val,
        stage="val",
        key=val_key,
        step_tracker=step_tracker,
        logger=logger,
    )
    test_dataloader = get_dataloader(
        cfg,
        batch_size=batch_size_test or batch_size_train_val,
        stage="test",
        key=test_key,
        step_tracker=step_tracker,
        logger=logger,
    )

    return train_dataloader, val_dataloader, test_dataloader
