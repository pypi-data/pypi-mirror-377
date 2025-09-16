from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

import equinox as eqx
from jaxtyping import PRNGKeyArray

from src.dataset.types import UnbatchedInput


@dataclass
class SequenceMixerBaseConfig:
    name: str


class SequenceMixer(eqx.Module, ABC):
    @abstractmethod
    def __init__(
        self,
        cfg: SequenceMixerBaseConfig,
        input_dim: int,
        key: PRNGKeyArray,
        **kwargs,
    ):
        pass

    def filter_spec_lambda(self) -> Callable[..., bool]:
        return lambda _: True

    @abstractmethod
    def __call__(self, input_sequence: UnbatchedInput) -> UnbatchedInput:
        pass
