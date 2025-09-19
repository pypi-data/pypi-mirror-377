from dataclasses import dataclass, field
from typing import List, Literal

import equinox as eqx
import jax
import jax.numpy as jnp
from jaxtyping import PRNGKeyArray

from stapax.dataset.types import EncoderOutput, UnbatchedTarget

from .types import Head, HeadBaseConfig

from .store import register_head


@dataclass
class ClassificationHeadConfig(HeadBaseConfig):
    name: Literal["classification"]
    metrics: List[str] = field(default_factory=lambda: ["accuracy"])


@register_head(cfg=ClassificationHeadConfig)
class ClassificationHead(Head):
    linear_layer: eqx.nn.Linear
    linear_layer_2: eqx.nn.Linear

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        cfg: ClassificationHeadConfig,
        *,
        key: PRNGKeyArray,
        **kwargs,
    ):
        l1_key, l2_key = jax.random.split(key, 2)
        self.name = cfg.name
        self.metrics = cfg.metrics
        self.linear_layer = eqx.nn.Linear(input_dim, input_dim, key=l1_key)
        self.linear_layer_2 = eqx.nn.Linear(input_dim, output_dim, key=l2_key)

    def __call__(self, x: EncoderOutput, key: PRNGKeyArray) -> UnbatchedTarget:
        x = jax.vmap(self.linear_layer)(x)  # shape (features,) -> (features,)
        x = jax.nn.relu(x)
        x = jax.vmap(self.linear_layer_2)(x)  # shape (features,) -> (classes,)
        x = jnp.mean(x, axis=0)  # shape (timesteps, features) -> (features,)
        x = jax.nn.log_softmax(x, axis=-1)

        return x
