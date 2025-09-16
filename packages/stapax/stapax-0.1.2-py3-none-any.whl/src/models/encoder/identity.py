from dataclasses import dataclass
from typing import Literal

import equinox as eqx
from jaxtyping import PRNGKeyArray


from .store import register_encoder
from src.dataset.types import UnbatchedInput, UnbatchedTarget
from src.models.encoder.types import Encoder, EncoderBaseConfig


@dataclass
class IdentityEncoderConfig(EncoderBaseConfig):
    name: Literal["identity"]
    number: int


@register_encoder(cfg=IdentityEncoderConfig)
class IdentityEncoder(Encoder):
    _output_dim: int

    def __init__(
        self,
        input_dim: int,
        cfg: IdentityEncoderConfig,
        **kwargs,
    ):
        self._output_dim = input_dim

    @property
    def output_dim(self) -> int:
        return self._output_dim

    def __call__(
        self,
        x: UnbatchedInput,
        state: eqx.nn.State,
        key: PRNGKeyArray,
    ) -> tuple[UnbatchedTarget, eqx.nn.State]:
        return x, state
