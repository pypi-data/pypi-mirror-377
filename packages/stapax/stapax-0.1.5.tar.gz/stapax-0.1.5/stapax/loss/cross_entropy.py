from dataclasses import dataclass
from typing import Literal

import jax.numpy as jnp
from jaxtyping import Scalar

from stapax.dataset.types import BatchedTarget
from stapax.loss.store import register_loss_function

from .types import AbstractLossFunction, BaseLossConfig


@dataclass
class CrossEntropyConfig(BaseLossConfig):
    name: Literal["cross_entropy"]
    for_each_timestep: bool = False


@register_loss_function(cfg=CrossEntropyConfig)
class CrossEntropy(AbstractLossFunction):
    @staticmethod
    def __call__(
        cfg: CrossEntropyConfig,
        true_y: BatchedTarget,
        pred_y: BatchedTarget,
    ) -> Scalar:
        # if true_y is one-hot encoded, we need to convert it back
        if true_y.ndim > 1 and not cfg.for_each_timestep:
            indices = jnp.argmax(true_y, axis=-1)
        else:
            # only batch dimension
            indices = true_y

        # Create a mask to ignore tokens marked with -100
        # -100 is commonly used as a padding/ignore token in NLP tasks
        # TODO: debug and print to check this is correct. I was not able to do this for jax reasons... @BEN, could you varify that jnp.sum(mask) = batch_size * num_tokens_to_copy?
        mask = indices != -100

        pred_y_at_target_index = jnp.take_along_axis(
            pred_y, jnp.expand_dims(indices, -1), axis=-1
        )

        # Apply the mask to exclude -100 tokens from loss computation
        # need to do the awkward jnp.where for jax reasons...
        masked_pred_y = jnp.where(mask[..., None], pred_y_at_target_index, 0.0)

        # divide by the valid tokens to get the mean loss
        return cfg.weight * -jnp.sum(masked_pred_y) / jnp.sum(mask)
