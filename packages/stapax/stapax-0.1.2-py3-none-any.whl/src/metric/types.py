from typing import Callable, List, Literal, Tuple

import jax.numpy as jnp
from pytorch_lightning import Callback, LightningModule, Trainer

from src.dataset.types import Batch, UnbatchedTarget
from src.types import JaxLightningStepOutput

Metric = Callable[[UnbatchedTarget, UnbatchedTarget], float]


class CustomMetric(Callback):
    """
    Helper class to handle metric logging for each head.
    """

    def __init__(
        self,
        heads: List[Tuple[str, int]],  # (head_name, head_index)
        metric: Metric,
        metric_name: str,
        prog_bar: bool = False,
    ):
        super().__init__()
        self.metric = metric
        self.metric_name = metric_name
        self.heads = heads
        self.prog_bar = prog_bar

    def log_metric(
        self,
        trainer: Trainer,
        pl_module: LightningModule,
        outputs: JaxLightningStepOutput,  # for each head
        batch: Batch,
        batch_idx: int,
        stage: Literal["train", "val", "test"],
    ) -> None:
        inputs, target = batch["input"], batch["target"]
        params = batch.get("params", None)

        model_outputs = outputs["outputs"]

        n_heads = len(target)
        for head_name, head_index in self.heads:
            head_output = model_outputs[head_index]
            head_target = target[head_index % n_heads]

            metric_value = self.metric(
                target=head_target,
                pred=head_output,
                params=params,
                input=inputs,
            )

            if isinstance(metric_value, jnp.ndarray):
                metric_value = metric_value.item()

            pl_module.log(
                f"{stage}/{head_name}/{self.metric_name}",
                metric_value,
                prog_bar=self.prog_bar,
                batch_size=inputs.shape[0],
            )

    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        self.log_metric(trainer, pl_module, outputs, batch, batch_idx, stage="train")

    def on_validation_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        self.log_metric(trainer, pl_module, outputs, batch, batch_idx, stage="val")

    def on_test_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        self.log_metric(trainer, pl_module, outputs, batch, batch_idx, stage="test")
