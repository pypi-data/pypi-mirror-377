from abc import abstractmethod
from dataclasses import dataclass
from typing import Callable

import equinox as eqx
import jax.numpy as jnp
from jaxtyping import PRNGKeyArray

from stapax.dataset.types import EncoderOutput, UnbatchedInput
from stapax.models.sequence_mixer.types import SequenceMixer


@dataclass
class EncoderBaseConfig:
    name: str


class Encoder(eqx.Module):
    """
    Abstract base class for all encoders.

    This class is used to define the interface for all encoders.
    """

    @abstractmethod
    def __init__(
        self,
        input_dim: int,
        cfg: EncoderBaseConfig,
        input_dtype: jnp.dtype,
        key: PRNGKeyArray,
        sequence_mixer: SequenceMixer | None = None,
        num_embeddings: int | None = None,
        **kwargs,
    ) -> None:
        pass

    @abstractmethod
    def __call__(
        self, x: UnbatchedInput, state: eqx.nn.State, key: PRNGKeyArray
    ) -> tuple[EncoderOutput, eqx.nn.State]:
        pass

    def filter_spec_lambda(self) -> Callable[..., bool]:
        return lambda _: True

    @property
    @abstractmethod
    def output_dim(self) -> int:
        pass
