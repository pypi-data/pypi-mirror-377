from dataclasses import dataclass, field
from typing import List, Literal

import equinox as eqx
import jax
from jaxtyping import PRNGKeyArray

from src.dataset.types import UnbatchedInput, UnbatchedTarget

from .types import Head, HeadBaseConfig

from .store import register_head


@dataclass
class MultiClassHeadConfig(HeadBaseConfig):
    name: Literal["multiclass"]
    metrics: List[str] = field(default_factory=lambda: ["masked_accuracy"])


@register_head(cfg=MultiClassHeadConfig)
class MultiClassHead(Head):
    linear_layer: eqx.nn.Linear

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        cfg: MultiClassHeadConfig,
        *,
        key: PRNGKeyArray,
        **kwargs,
    ):
        self.name = cfg.name
        self.metrics = cfg.metrics
        self.linear_layer = eqx.nn.Linear(input_dim, output_dim, key=key)

    def __call__(self, x: UnbatchedInput, key: PRNGKeyArray) -> UnbatchedTarget:
        x = jax.vmap(self.linear_layer)(x)  # shape (T, input_dim) -> (T, output_dim)

        # now x has shape T x output_dim. Apply softmax across the last dimension
        x = jax.nn.log_softmax(x, axis=-1)
        return x
