from dataclasses import asdict, dataclass
from typing import Literal

import optax


@dataclass
class CosineOneCycleWarmupCfg:
    name: Literal["warmup_cosine_decay_schedule"]
    init_value: float
    peak_value: float
    warmup_steps: int
    decay_steps: int


@dataclass
class CosineOneCycleCfg:
    name: Literal["cosine_decay_schedule"]
    init_value: float
    alpha: float
    decay_steps: int


@dataclass
class ConstantCfg:
    name: Literal["constant"]
    value: float


@dataclass
class ExponentialDecayCfg:
    name: Literal["exponential_decay"]
    init_value: float
    transition_steps: int
    decay_rate: float


LR_SCHEDULES = {
    "warmup_cosine_decay_schedule": optax.schedules.warmup_cosine_decay_schedule,
    "constant": optax.constant_schedule,
    "exponential_decay": optax.exponential_decay,
    "cosine_decay_schedule": optax.schedules.cosine_decay_schedule,
}

LRScheduleCfgs = (
    CosineOneCycleWarmupCfg
    | ConstantCfg
    | CosineOneCycleCfg
    | ExponentialDecayCfg
    | int
    | float
)


def get_learning_rate_schedule(cfg: LRScheduleCfgs) -> optax.Schedule:
    if isinstance(cfg, (int, float)):
        return LR_SCHEDULES["constant"](value=cfg)
    cfg_dict = asdict(cfg)
    name = cfg_dict.pop("name")
    return LR_SCHEDULES[name](**cfg_dict)
