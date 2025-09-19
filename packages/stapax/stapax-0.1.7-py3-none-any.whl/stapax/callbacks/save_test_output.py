import os
from pathlib import Path

import numpy as np
import pytorch_lightning as pl

from stapax.dataset.types import Batch
from stapax.types import JaxLightningStepOutput


class CollectTestOutputsCallback(pl.Callback):
    def __init__(self, save_dir: str):
        super().__init__()
        self.save_dir = Path(save_dir)
        self.outputs = []
        self.inputs = []
        self.targets = []

    def on_test_batch_end(
        self,
        trainer: pl.Trainer,
        pl_module: pl.LightningModule,
        outputs: JaxLightningStepOutput,
        batch: Batch,
        batch_idx: int,
        dataloader_idx=0,
    ):
        """
        Called when the test batch ends.
        `outputs` is whatever your LightningModule's `test_step` returns.
        """

        model_outputs = outputs["outputs"]
        inputs, targets = batch["input"], batch["target"]

        self.outputs.extend(model_outputs)
        self.inputs.extend(inputs)
        self.targets.extend(targets)

    def on_test_end(self, trainer: pl.Trainer, pl_module: pl.LightningModule):
        """
        Called at the end of the test epoch.
        Saves all collected outputs into numpy array
        """
        self.outputs = np.array(self.outputs)
        self.inputs = np.array(self.inputs)
        self.targets = np.array(self.targets)

        os.makedirs(self.save_dir, exist_ok=True)
        np.savez(
            self.save_dir / "test_output.npz",
            outputs=self.outputs,
            inputs=self.inputs,
            targets=self.targets,
        )

        print(f"Test outputs saved to {self.save_dir}")
