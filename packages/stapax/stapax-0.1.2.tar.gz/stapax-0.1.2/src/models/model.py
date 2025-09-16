from dataclasses import dataclass
from typing import Callable, List, Tuple

import equinox as eqx
import jax.random as jr
from jaxtyping import PRNGKeyArray

from src.dataset.types import UnbatchedInput, UnbatchedTarget

from src.models.encoder import EncoderConfig
from src.models.encoder.types import Encoder
from src.models.heads import HeadConfig
from src.models.heads.types import Head
from src.models.sequence_mixer import SequenceMixerConfig


@dataclass
class ModelConfig:
    encoder: EncoderConfig
    heads: List[HeadConfig]
    sequence_mixer: SequenceMixerConfig | None = None


class Model(eqx.Module):
    encoder: Encoder
    heads: List[Head]

    def __init__(
        self,
        encoder: Encoder,
        heads: List[Head],
    ):
        self.encoder = encoder
        self.heads = heads

    def __call__(
        self,
        x: UnbatchedInput,
        state: eqx.nn.State,
        key: PRNGKeyArray,
    ) -> tuple[Tuple[UnbatchedTarget, ...], eqx.nn.State]:
        key, encoder_key = jr.split(key, 2)
        y, state = self.encoder(x, state=state, key=key)

        key, head_keys = jr.split(key, len(self.heads) + 1)
        outputs = []
        for head, h_key in zip(self.heads, head_keys):
            outputs.append(head(y, key=h_key))

        return tuple(outputs), state

    def filter_spec_lambda(self) -> Callable[..., bool]:
        return lambda _: True
