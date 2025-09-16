from dataclasses import asdict, dataclass, field
import logging
from pathlib import Path
from typing import Any, Literal, Type, TypeVar
import importlib.resources

from dacite import Config, from_dict
from omegaconf import DictConfig, OmegaConf

from stapax.dataset import DatasetConfig
from stapax.misc.learning_rate import LRScheduleCfgs
from stapax.misc.save_checkpoint import CheckpointCfg

from .models import ModelConfig

OmegaConf.register_new_resolver("multiply", lambda x, y: x * y)
OmegaConf.register_new_resolver("divide", lambda x, y: x / y)
OmegaConf.register_new_resolver(
    "total_steps",
    lambda num_examples, batch_size, epochs: (int(num_examples) // int(batch_size))
    * int(epochs),
)


def get_config_dir() -> Path:
    """Get the path to the config directory in the installed package."""
    # Try relative path from this file (development)
    rel_config_path = Path(__file__).parent / "configs"
    if rel_config_path.exists():
        return rel_config_path

    # Try to get the config directory from the package
    try:
        return importlib.resources.files("stapax").joinpath("configs")
    except Exception:
        # Final fallback
        return Path("configs")


@dataclass
class TestCfg:
    output_path: Path = Path("results")
    batch_size: int | None = None


@dataclass
class WandbCfg:
    name: str
    project: str
    mode: Literal["online", "offline", "shared", "disabled", "dryrun", "run"] = (
        "offline"
    )
    tags: list[str] = field(default_factory=list)
    notes: str | None = None


@dataclass
class EarlyStoppingCfg:
    metric: str = "val/mse"
    min_delta: float = 0.0
    patience: int = 20
    verbose: bool = True
    mode: Literal["min", "max"] = "min"
    warmup_steps: int | None = None


@dataclass
class TrainCfg:
    lr: LRScheduleCfgs
    batch_size: int
    val_check_interval: float = 1.0
    check_val_every_n_epoch: int | None = 1
    log_every_n_steps: int = 25
    clip_grad_global_norm: float | None = None
    weight_decay: float | None = None
    checkpoint: CheckpointCfg = field(default_factory=CheckpointCfg)
    early_stopping: EarlyStoppingCfg | None = None
    max_steps: int = -1  # -1 is no limit
    max_epochs: int = -1  # -1 is no limit
    min_steps: int | None = None
    min_epochs: int | None = None

    def __post_init__(self):
        # Validate configuration. Note that -1 is used in PyTorch Lightningto indicate that the max/min steps/epochs are not set.
        if self.max_steps != -1 and self.max_epochs != -1:
            raise ValueError(
                "Both max_steps and max_epochs are defined in the config. Please specify only one."
            )
        if self.min_steps is not None and self.min_epochs is not None:
            raise ValueError(
                "Both min_steps and min_epochs are defined in the config. Please specify only one."
            )


@dataclass
class RootCfg:
    wandb: WandbCfg
    mode: Literal["train", "test", "all"]
    model: ModelConfig
    train: TrainCfg
    test: TestCfg
    dataset: DatasetConfig
    seed: int = 42
    load_from_checkpoint: Path | None = None
    output_dir: Path | None = None
    use_compilation_cache: bool = True
    sweep_on_test: bool = False
    log_level: int = logging.INFO

    def to_dict(self) -> dict:
        as_dict = asdict(self)

        def _stringify(value: Any) -> Any:
            if isinstance(value, Path):
                return str(value)
            elif isinstance(value, dict):
                return {k: _stringify(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [_stringify(v) for v in value]
            elif isinstance(value, tuple):
                return tuple(_stringify(v) for v in value)
            elif isinstance(value, object):
                return str(value)
            return value

        return _stringify(as_dict)


TYPE_HOOKS = {
    Path: Path,
}


T = TypeVar("T")


def load_typed_config(
    cfg: DictConfig,
    data_class: Type[T],
    extra_type_hooks: dict = {},
) -> T:
    return from_dict(
        data_class,
        OmegaConf.to_container(cfg, resolve=True),
        config=Config(type_hooks={**TYPE_HOOKS, **extra_type_hooks}),
    )


def load_typed_root_config(cfg: DictConfig, configType: Type[T] = RootCfg) -> T:
    return load_typed_config(
        cfg,
        configType,
        {},
    )
