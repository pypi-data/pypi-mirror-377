import logging
import uuid
from pathlib import Path
import coloredlogs
from pytorch_lightning.loggers import Logger, WandbLogger

from stapax.config import RootCfg
from stapax.logging.local_logger import LocalLogger


def setup_logging(level: int = logging.DEBUG):
    logger = logging.getLogger()
    logger.setLevel(level)

    # Avoid duplicate handlers if setup_logging() is called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(level)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(name)s: %(message)s",
        "%H:%M:%S",
    )
    console.setFormatter(formatter)
    logger.addHandler(console)

    # Optional: add coloredlogs on top of standard logging
    coloredlogs.install(level=level, logger=logger)

    return logger


def get_lightning_logger(cfg: RootCfg, output_dir: Path, is_multirun: bool) -> Logger:
    # create wandb tags
    wandb_tags = (
        [cfg.mode, cfg.model.encoder.name, cfg.dataset.name]
        + cfg.wandb.tags
        + [head.name for head in cfg.model.heads]
    )
    if hasattr(cfg.model.encoder, "sequence_mixer"):
        wandb_tags += [cfg.model.encoder.sequence_mixer.name]
    if hasattr(cfg.dataset, "task"):
        wandb_tags += [cfg.dataset.task]

    cfg.wandb.tags = wandb_tags

    # create a meaningful name for the wandb run
    wandb_name = cfg.model.encoder.name
    if hasattr(cfg.model.encoder, "sequence_mixer"):
        wandb_name += "/" + cfg.model.encoder.sequence_mixer.name
    wandb_name += "/" + cfg.dataset.name
    if hasattr(cfg.dataset, "task"):
        wandb_name += "/" + cfg.dataset.task
    if hasattr(cfg.dataset, "seq_len"):
        wandb_name += "/" + str(cfg.dataset.seq_len)

    # initialize logger
    logger = (
        WandbLogger(
            project=cfg.wandb.project,
            name=wandb_name,
            mode=cfg.wandb.mode,
            tags=cfg.wandb_tags,
            notes=cfg.wandb.notes,
            save_dir=output_dir,
            config=cfg.to_dict(),
            log_model=False,
            group=(
                "_".join(wandb_tags) + "_" + str(uuid.uuid4())[:8]
                if is_multirun
                else None
            ),
        )
        if cfg.wandb.mode != "disabled"
        else LocalLogger(config=cfg.to_dict())
    )

    return logger
