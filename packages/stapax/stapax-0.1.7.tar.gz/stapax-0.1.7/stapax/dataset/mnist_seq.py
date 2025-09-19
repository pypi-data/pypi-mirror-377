from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Tuple

import jax.numpy as jnp
import numpy as np
from jaxtyping import Array, Float
from matplotlib import pyplot as plt

from .types import (
    AbstractDatasetConfig,
    ShimedDatasetItem,
    Stage,
    StandardDataset,
    UnbatchedInput,
    UnbatchedTarget,
)

from stapax.dataset.store import register_dataset


@dataclass
class MNISTSeqConfig(AbstractDatasetConfig):
    name: Literal["mnist_seq"]
    train_val_split: float = 0.8
    timesteps: int = 128


@register_dataset(cfg=MNISTSeqConfig)
class MNISTSeq(StandardDataset):
    def __init__(self, cfg: MNISTSeqConfig, stage: Stage, **kwargs) -> None:
        self.cfg = cfg
        self.stage = stage

        # Ensure preprocessed data exists
        if (
            not (cfg.root_path / "test_data.npy").exists()
            or not (cfg.root_path / "train_data.npy").exists()
        ):
            self._preprocess()

        # Load data and labels for this stage
        self.data, self.labels = self._load_dataset(stage)

    def _load_dataset(self, stage: Stage) -> Tuple[jnp.ndarray, np.ndarray]:
        """Load data and labels for the specified stage."""
        if stage == "test":
            data = np.load(self.cfg.root_path / "test_data.npy")
            labels = np.loadtxt(self.cfg.root_path / "testlabels.txt", dtype=int)
            return data, labels

        # For train and val, we need to split the training data
        data = np.load(self.cfg.root_path / "train_data.npy")
        labels = np.loadtxt(self.cfg.root_path / "trainlabels.txt", dtype=int)

        # Split point
        split_idx = int(len(labels) * self.cfg.train_val_split)

        if stage == "train":
            return data[:split_idx], labels[:split_idx]
        elif stage == "val":
            return data[split_idx:], labels[split_idx:]
        else:
            raise ValueError(f"Invalid stage: {stage}")

    def _preprocess(self):
        """
        Read all test/train files and save as preprocessed arrays.
        Pad all sequences to the same length (128).
        """
        print("Preprocessing MNIST data...")

        # Process test data
        test_files = list(self.cfg.root_path.glob("testimg-*-inputdata.txt"))

        if len(test_files) == 0:
            raise ValueError("No files found at path: ", self.cfg.root_path)

        # Sort by the numerical index in the filename
        test_files.sort(key=lambda x: int(x.stem.split("-")[1]))

        test_data = []
        for file in test_files:
            data = np.loadtxt(file)
            data = np.pad(data, ((0, self.cfg.timesteps - data.shape[0]), (0, 0)))
            test_data.append(data)
        test_data = np.stack(test_data)
        np.save(self.cfg.root_path / "test_data.npy", test_data)

        # Process train data
        train_files = list(self.cfg.root_path.glob("trainimg-*-inputdata.txt"))
        # Sort by the numerical index in the filename
        train_files.sort(key=lambda x: int(x.stem.split("-")[1]))

        train_data = []
        for file in train_files:
            data = np.loadtxt(file)
            data = np.pad(data, ((0, self.cfg.timesteps - data.shape[0]), (0, 0)))
            train_data.append(data)
        train_data = np.stack(train_data)
        np.save(self.cfg.root_path / "train_data.npy", train_data)

        print("Done preprocessing MNIST data.")

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, index: int) -> ShimedDatasetItem:
        # Convert label to one-hot encoding
        onehot_labels = np.zeros(10)
        onehot_labels[self.labels[index]] = 1

        data = self.data[index]

        return ShimedDatasetItem(
            input=data,
            target=onehot_labels,
        )

    @staticmethod
    def convert_sample(
        sample: Float[Array, "sequence_length 4"],
    ) -> Float[Array, "sequence_length 4"]:
        """
        The four features are:
        - dx: change in x coordinate (implicit starting point is (0, 0))
        - dy: change in y coordinate
        - end of stroke: 1 if the stroke ends, 0 otherwise
        - end of digit: 1 if the sequence ends, 0 otherwise

        This functions converts the sample into a sequence of features.
        - x: coordinate
        - y: coordinate
        - end of stroke: 1 if the stroke ends, 0 otherwise
        - end of digit: 1 if the sequence ends, 0 otherwise

        The sequence length is the number of strokes in the sample.
        """
        x = np.cumsum(sample[:, 0])
        y = np.cumsum(sample[:, 1])
        end_of_stroke = np.concatenate([[0], np.diff(sample[:, 2])])
        end_of_digit = np.concatenate([[0], np.diff(sample[:, 3])])
        return np.stack([x, y, end_of_stroke, end_of_digit], axis=1)

    @staticmethod
    def plot(
        X: UnbatchedInput,
        y: UnbatchedTarget,
        output: UnbatchedTarget,
        path: Path | str | None = None,
    ) -> None:
        """
        Plot the first 16 samples in the batch.
        """
        # convert sequences back to images by drawing the stroke on a 28 x 28 canvas
        # arrange in 4x4 grid
        fig, axs = plt.subplots(4, 4, figsize=(10, 10))
        for i, (sample, label, output, ax) in enumerate(
            zip(
                X,
                y,
                jnp.exp(output),
                axs.flatten(),
            )
        ):
            empty_canvas = np.zeros((29, 29))
            s = MNISTSeq.convert_sample(sample)
            for x1, x2 in zip(s[:, 0], s[:, 1]):
                empty_canvas[int(x2), int(x1)] = 1
            ax.imshow(empty_canvas, cmap="gray")
            ax.set_title(f"{i}: Label {np.argmax(label)}, Pred {np.argmax(output)}")
        if path is not None:
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(path)
        else:
            plt.show()

    @property
    def target_feature_dim(self) -> int:
        return 10

    @property
    def input_feature_dim(self) -> int:
        return 4

    @property
    def dtype(self) -> jnp.dtype:
        return jnp.float32

    @property
    def input_timesteps(self) -> int:
        return self.cfg.timesteps

    @property
    def num_embeddings(self) -> int:
        return 10


if __name__ == "__main__":
    cfg = MNISTSeqConfig(
        name="mnist_seq",
        root_path=Path("data/MNIST_sequences"),
        shuffle=False,
    )
    dataset = MNISTSeq(cfg, "train")
    print(len(dataset))
    print(dataset[0]["input"].shape, dataset[0]["target"].shape)  # (46, 4) (10,)
    val_dataset = MNISTSeq(cfg, "val")
    print(len(val_dataset))
    print(dataset[0]["input"].shape, dataset[0]["target"].shape)  # (46, 4) (10,)
    dataset = MNISTSeq(cfg, "test")
    print(len(dataset))
    print(dataset[0]["input"].shape, dataset[0]["target"].shape)  # (46, 4) (10,)

    # create a batch of 16 samples and plot them
    batch = [dataset[i] for i in range(16)]
    X, y = zip(*batch)
    MNISTSeq.plot(X, y, np.zeros((16, 10)))
