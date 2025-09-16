from dataclasses import dataclass
from typing import Literal

import jax.numpy as jnp
from jaxtyping import Scalar

from src.dataset.types import BatchedTarget
from src.loss.store import register_loss_function
from .types import AbstractLossFunction, BaseLossConfig


@dataclass
class GatedRegressionConfig(BaseLossConfig):
    name: Literal["gated_regression"]
    weights: tuple[float, float] = (1e-4, 1e-4)


@register_loss_function(cfg=GatedRegressionConfig)
class GatedRegression(AbstractLossFunction):
    @staticmethod
    def __call__(
        cfg: GatedRegressionConfig,
        true_y: BatchedTarget,
        pred_y: BatchedTarget,
    ) -> Scalar:
        """
        Apply mse to the distance to the signal if the true label is a signal
        else loss = exp(-w[1] * pred_y)
        """

        # jax.debug.print("true_dist: {}", true_y.flatten())
        # jax.debug.print("pred_dist: {}", pred_y.flatten())

        is_signal = true_y > 0
        # jax.debug.print("is_signal: {}", is_signal)
        target = jnp.abs(true_y)
        # jax.debug.print("target: {}", target)

        # punish examples that are far from the signal less
        factor = jnp.where(is_signal, jnp.exp(-cfg.weights[0] * target), 0)
        # jax.debug.print("factor: {}", factor)
        # jax.debug.print("l1.1: {}", jnp.square(pred_y - target) * factor)

        l1 = (
            cfg.weights[0]
            * jnp.sum(jnp.square(pred_y - target) * factor)
            / jnp.sum(is_signal)
        )

        # l2 = (
        #     1
        #     / cfg.weights[1]
        #     * jnp.sum(~is_signal * jnp.exp(-cfg.weights[1] * pred_y))
        #     / jnp.sum(~is_signal)
        # )
        # jax.debug.print("l2.1: {}", ~is_signal * jnp.exp(-cfg.weights[1] * target))
        # jax.debug.print("l1: {} l2: {}", l1, l2)

        return l1  # + l2
