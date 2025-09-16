from dataclasses import dataclass
from typing import Literal

import jax.numpy as jnp
from jaxtyping import Scalar

from src.dataset.types import BatchedTarget
from src.loss.store import register_loss_function
from .types import AbstractLossFunction, BaseLossConfig


@dataclass
class MSEConfig(BaseLossConfig):
    name: Literal["mse"]
    index: int | None = None


@register_loss_function(cfg=MSEConfig)
class MSE(AbstractLossFunction):
    @staticmethod
    def __call__(
        cfg: MSEConfig,
        true_y: BatchedTarget,
        pred_y: BatchedTarget,
    ) -> Scalar:
        if cfg.index is not None:
            true_y = true_y[..., cfg.index]
            pred_y = pred_y[..., cfg.index]
        return cfg.weight * jnp.mean((true_y - pred_y) ** 2)
