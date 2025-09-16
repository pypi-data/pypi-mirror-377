from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Tuple, TypedDict

import jax.numpy as jnp
from jaxtyping import Array, Float, PRNGKeyArray
from pytorch_lightning import Callback
from pytorch_lightning.loggers import Logger
from torch.utils.data import DataLoader
from torch.utils.data import Dataset as TorchDataset

from src.misc.step_tracker import StepTracker

Stage = Literal["train", "val", "test"]

UnbatchedInput = Float[Array, "timesteps features"]
BatchedInput = Float[UnbatchedInput, "batch_size"]

EncoderOutput = Float[Array, "timesteps features"]
BatchedEncoderOutput = Float[EncoderOutput, "batch_size"]

UnbatchedTarget = Float[Array, "output_features"]
BatchedTarget = Float[UnbatchedTarget, "batch_size"]

UnbatchedTargets = Tuple[UnbatchedTarget, ...]
BatchedTargets = Tuple[BatchedTarget, ...]

HeadOutput = Float[Array, "batch_size output_features"]
ModelOutput = Tuple[HeadOutput, ...]

UnbatchedParams = dict[str, Float[Array, "1"]]
BatchedParams = dict[str, Float[UnbatchedParams, " batch_size"]]


@dataclass
class DatasetItem:
    input: UnbatchedInput
    target: UnbatchedTarget
    params: UnbatchedParams | None


class ShimedDatasetItem(DatasetItem):
    input: UnbatchedInput
    target: Tuple[UnbatchedTarget, ...]
    params: UnbatchedParams | None

    def __init__(
        self,
        input: UnbatchedInput,
        target: Tuple[UnbatchedTarget, ...] | UnbatchedTarget,
        params: UnbatchedParams | None = None,
    ):
        super().__init__(input, target, params)

        if isinstance(target, (tuple, list)):
            self.target = target
        else:
            self.target = (target,)


@dataclass
class AbstractDatasetConfig:
    name: str
    root_path: Path
    shuffle: bool
    num_workers: int = field(default=4, init=False)


class Batch(TypedDict):
    input: BatchedInput
    target: BatchedTargets
    params: BatchedParams | None


class StandardDataset(TorchDataset, ABC):
    @abstractmethod
    def __init__(
        self,
        cfg: AbstractDatasetConfig,
        stage: Stage,
        step_tracker: StepTracker | None,
        key: PRNGKeyArray,
    ) -> None:
        pass

    @abstractmethod
    def __getitem__(self, index: int) -> ShimedDatasetItem:
        pass

    @property
    @abstractmethod
    def input_feature_dim(self) -> int:
        """The number of features in the input data. Needs to be implemented by the dataset."""
        pass

    @property
    @abstractmethod
    def input_timesteps(self) -> int:
        """The number of timesteps in the input data. Needs to be implemented by the dataset."""
        pass

    @property
    @abstractmethod
    def target_feature_dim(self) -> int:
        """The number of classes in the output data. Needs to be implemented by the dataset."""
        pass

    @property
    @abstractmethod
    def dtype(self) -> jnp.dtype:
        """The dtype of the input data. Needs to be implemented by the dataset."""
        pass

    @property
    def callbacks(self) -> list[Callback]:
        """
        Returns a list of callbacks e.g. for visualization etc.
        """
        return []

    @property
    def num_embeddings(self) -> int | None:
        """The number of embeddings in the input data. Needs to be implemented by the dataset."""
        return None


class CustomDataloader(DataLoader):
    """
    Custom dataloader with extra properties

    - input_dim: int
    - output_dim: int
    - timesteps: int
    - dtype: jnp.dtype
    """

    input_feature_dim: int
    target_feature_dim: int
    input_timesteps: int
    dtype: jnp.dtype
    callbacks: list[Callback]
    num_embeddings: int | None

    def __init__(
        self,
        input_feature_dim: int,
        target_feature_dim: int,
        input_timesteps: int,
        dtype: jnp.dtype,
        callbacks: list[Callback],
        num_embeddings: int | None,
        logger: Logger | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.input_feature_dim = input_feature_dim
        self.target_feature_dim = target_feature_dim
        self.input_timesteps = input_timesteps
        self.dtype = dtype
        self.callbacks = callbacks
        self.logger = logger
        self.num_embeddings = num_embeddings
