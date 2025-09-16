from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List

import equinox as eqx
from jaxtyping import PRNGKeyArray

from src.dataset.types import (
    EncoderOutput,
    UnbatchedTarget,
)
from src.loss import LossConfig


@dataclass
class HeadBaseConfig:
    name: str
    loss_fns: List[LossConfig]
    output_dim: int | None = None
    metrics: List[str] = field(default_factory=lambda: [])


class Head(eqx.Module, ABC):
    name: str
    metrics: List[str]

    @abstractmethod
    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        cfg: HeadBaseConfig,
        *,
        key: PRNGKeyArray,
        **kwargs,
    ):
        pass

    @abstractmethod
    def __call__(self, x: EncoderOutput, key: PRNGKeyArray) -> UnbatchedTarget:
        pass
