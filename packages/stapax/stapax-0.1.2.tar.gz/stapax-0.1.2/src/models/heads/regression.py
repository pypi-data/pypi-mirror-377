from dataclasses import dataclass, field
from typing import List, Literal

import equinox as eqx
import jax
import jax.numpy as jnp
from jaxtyping import PRNGKeyArray

from src.dataset.types import UnbatchedInput, UnbatchedTarget

from .types import Head, HeadBaseConfig

from .store import register_head


@dataclass
class RegressionHeadConfig(HeadBaseConfig):
    name: Literal["regression"]
    linear_output: bool = False
    output_step: int = 1
    metrics: List[str] = field(default_factory=lambda: ["mse", "rel_mse", "l1_loss"])


@register_head(cfg=RegressionHeadConfig)
class RegressionHead(Head):
    linear_layer: eqx.nn.Linear
    # linear_layer_2: eqx.nn.Linear
    # time_layer: eqx.nn.Linear
    output_step: int
    linear_output: bool
    is_gaussian_nll: bool

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        cfg: RegressionHeadConfig,
        *,
        key: PRNGKeyArray,
        timesteps: int,
        **kwargs,
    ):
        self.name = cfg.name
        self.output_step = cfg.output_step
        self.linear_output = cfg.linear_output
        self.metrics = cfg.metrics
        self.is_gaussian_nll = "gaussian_nll" in [
            loss_fn.name for loss_fn in cfg.loss_fns
        ]
        if cfg.output_dim is not None and cfg.output_dim != input_dim:
            print(
                f"Manually overriding {cfg.name} head output_dim to {cfg.output_dim} (dataset natural output dim is {output_dim})"
            )
            output_dim = cfg.output_dim
        self.linear_layer = eqx.nn.Linear(input_dim, output_dim, key=key)
        # self.linear_layer_2 = eqx.nn.Linear(cfg.hidden_dim, output_dim, key=key)
        # self.time_layer = eqx.nn.Linear(timesteps, 1, key=key)

    def __call__(self, x: UnbatchedInput, key: PRNGKeyArray) -> UnbatchedTarget:
        # x = x[self.output_step - 1 :: self.output_step]
        # x = jax.vmap(self.linear_layer_2)(x)[-1]
        # x = jax.nn.relu(x)
        # if not self.linear_output:
        #     x = jax.nn.tanh(x)
        # x = jax.vmap(self.time_layer)(x.T).T
        x = x.mean(axis=0)
        x = self.linear_layer(x)  # (batch, 6) -> (batch, 4) # 6*4 = 24/36

        if self.is_gaussian_nll:
            # apply softplus to second half of last dimensino
            x1, x2 = jnp.split(x, 2, axis=-1)
            x2 = jax.nn.softplus(x2)
            x = jnp.concatenate([x1, x2], axis=-1)

        return x
