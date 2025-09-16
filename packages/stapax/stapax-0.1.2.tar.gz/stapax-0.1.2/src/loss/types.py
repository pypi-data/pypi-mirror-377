from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Callable

from jaxtyping import Scalar

from src.dataset.types import BatchedTarget

LossFunction = Callable[[BatchedTarget, BatchedTarget], Scalar]


@dataclass
class BaseLossConfig:
    name: str
    weight: float = field(default=1.0, init=False)


class AbstractLossFunction:
    """
    Abstract base class for all losses.

    This class is used to define the interface for all losses.
    """

    @abstractmethod
    def __call__(
        cfg: BaseLossConfig,
        true_y: BatchedTarget,
        pred_y: BatchedTarget,
    ) -> Scalar:
        pass
