from typing import Any, List

import equinox as eqx
import jax
import jax.numpy as jnp
import optax
import pytorch_lightning as pl
from jaxtyping import PRNGKeyArray

from stapax.config import TestCfg, TrainCfg
from stapax.dataset.types import (
    Batch,
    BatchedInput,
    BatchedTargets,
    ModelOutput,
)
from stapax.loss.types import LossFunction
from stapax.misc.step_tracker import StepTracker
from stapax.models.model import Model
from stapax.optimizer import get_optimizer
from stapax.types import JaxLightningStepOutput


class JaxLightningWrapper(pl.LightningModule):
    config: TrainCfg
    model: Model
    model_state: eqx.nn.State
    model_filter_spec: dict[str, bool]
    test_config: TestCfg
    train_config: TrainCfg
    step_tracker: StepTracker
    loss_fns: List[LossFunction]

    def __init__(
        self,
        model: Model,
        model_state: eqx.nn.State,
        model_filter_spec: dict[str, bool],
        test_config: TestCfg,
        train_config: TrainCfg,
        loss_fns: List[LossFunction],
        step_tracker: StepTracker,
        key: PRNGKeyArray,
    ):
        super().__init__()
        # we need to manually call the optimizer step using Optax instead of the lightning trainer
        self.automatic_optimization = False

        self.model = model
        self.model_state = model_state
        self.model_filter_spec = model_filter_spec
        self.test_config = test_config
        self.train_config = train_config
        self.loss_fns = loss_fns
        self.step_tracker = step_tracker

        self.key, self.train_key, self.val_key, self.test_key = jax.random.split(key, 4)

        self.configure_optimizers()

    def configure_optimizers(self):
        self.optim, self.opt_state, self.lr_schedule = get_optimizer(
            self.train_config, self.model
        )

    def training_step(self, batch: Batch) -> JaxLightningStepOutput:
        X, y = batch["input"], batch["target"]
        params = batch.get("params", None)

        # with jax.profiler.trace("scratch/jax-trace", create_perfetto_link=True):
        (
            self.model,
            self.model_state,
            self.opt_state,
            loss,
            outputs,
            grad_norms_mean,
            grad_norms_max,
        ) = JaxLightningWrapper.apply_training_step(
            model=self.model,
            model_filter_spec=self.model_filter_spec,
            model_state=self.model_state,
            X=X,
            y=y,
            loss_fns=self.loss_fns,
            key=self.train_key,
            opt_state=self.opt_state,
            opt_update=self.optim.update,
        )
        # outputs.block_until_ready()

        self.log("train/grad_norms_mean", grad_norms_mean.item(), prog_bar=True)
        self.log("train/grad_norms_max", grad_norms_max.item(), prog_bar=True)
        self.log("train/loss", loss.item(), prog_bar=True)
        lr = self.lr_schedule(self.global_step)
        if isinstance(lr, jax.Array):
            lr = lr.item()
        self.log("train/lr", lr, prog_bar=True)

        # this is needed for the lightning trainer to update the global step (https://github.com/ludwigwinkler/JaxLightning/issues/1)
        self.optimizers().step()
        self.step_tracker.set_step(self.global_step)

        return JaxLightningStepOutput(outputs=outputs, params=params)

    def validation_step(self, batch: Batch):
        X, y = batch["input"], batch["target"]
        params = batch.get("params", None)
        inference_model = eqx.tree_inference(self.model, value=True)
        diff_model, static_model = eqx.partition(
            inference_model, self.model_filter_spec
        )

        (loss, (_, outputs)), _ = eqx.filter_jit(JaxLightningWrapper.apply_loss_fn)(
            diff_model=diff_model,
            static_model=static_model,
            model_state=self.model_state,
            X=X,
            y=y,
            loss_fns=self.loss_fns,
            key=self.val_key,
        )

        self.log(
            "val/loss",
            jnp.asarray(loss).item(),
            prog_bar=True,
            batch_size=X.shape[0],
        )

        return JaxLightningStepOutput(outputs=outputs, params=params)

    def test_step(self, batch: Batch, batch_idx: int):
        X, y = batch["input"], batch["target"]
        params = batch.get("params", None)
        inference_model = eqx.tree_inference(self.model, value=True)
        # For validation, we don't update the model, just compute loss
        diff_model, static_model = eqx.partition(
            inference_model, self.model_filter_spec
        )

        (loss, (_, outputs)), _ = eqx.filter_jit(JaxLightningWrapper.apply_loss_fn)(
            diff_model=diff_model,
            static_model=static_model,
            model_state=self.model_state,
            X=X,
            y=y,
            loss_fns=self.loss_fns,
            key=self.test_key,
        )

        return JaxLightningStepOutput(outputs=outputs, params=params)

    @staticmethod
    def batched_forward(
        model: Model,
        X: BatchedInput,
        model_state: eqx.nn.State,
        key: PRNGKeyArray,
    ) -> tuple[ModelOutput, eqx.nn.State]:
        """
        Static (pure) function that vmaps over batch dimension.

        this function should be partially applied and returned
        """

        keys = jax.random.split(key, X.shape[0])
        outputs, model_state = jax.vmap(
            model,
            axis_name="batch",
            in_axes=(0, None, 0),
            out_axes=(0, None),
        )(X, model_state, keys)

        return outputs, model_state

    @staticmethod
    @eqx.filter_value_and_grad(has_aux=True)
    def apply_loss_fn(
        diff_model: Model,
        static_model: Model,
        model_state: eqx.nn.State,
        X: BatchedInput,
        y: BatchedTargets,
        loss_fns: List[LossFunction],
        key: PRNGKeyArray,
    ) -> tuple[jnp.ndarray, tuple[eqx.nn.State, ModelOutput]]:
        model = eqx.combine(diff_model, static_model)
        outputs, model_state = JaxLightningWrapper.batched_forward(
            model=model, X=X, model_state=model_state, key=key
        )

        loss = 0.0
        n_heads = len(loss_fns)
        for i, head_loss_fn in enumerate(loss_fns):
            # wrap around if there are more heads than targets
            loss += head_loss_fn(y[i % n_heads], outputs[i])

        return loss, (model_state, outputs)

    @staticmethod
    @eqx.filter_jit
    def apply_training_step(
        model: Model,
        model_filter_spec: dict[str, bool],
        model_state: Any,
        X: BatchedInput,
        y: BatchedTargets,
        loss_fns: List[LossFunction],
        key: PRNGKeyArray,
        opt_state: optax.OptState,
        opt_update: optax.TransformUpdateExtraArgsFn,
        **kwargs,
    ) -> tuple[
        Model, eqx.nn.State, optax.OptState, jnp.ndarray, ModelOutput, float, float
    ]:
        """
        Run model forward pass, compute loss and one optimizer step.

        To be autodiffed this needs to be a static (pure) function.
        """
        diff_model, static_model = eqx.partition(model, model_filter_spec)

        (loss, (new_model_state, output)), grads = JaxLightningWrapper.apply_loss_fn(
            diff_model,
            static_model=static_model,
            model_state=model_state,
            X=X,
            y=y,
            loss_fns=loss_fns,
            key=key,
        )

        grad_norms = jnp.array(
            [
                jnp.linalg.norm(x)
                for x in jax.tree.leaves(eqx.filter(grads, eqx.is_inexact_array))
            ]
        )

        grad_norms_mean = jnp.mean(grad_norms)
        grad_norms_max = jnp.max(grad_norms)

        updates, opt_state = opt_update(grads, opt_state, diff_model)
        model = eqx.apply_updates(diff_model, updates)
        model = eqx.combine(model, static_model)
        return (
            model,
            new_model_state,
            opt_state,
            loss,
            output,
            grad_norms_mean,
            grad_norms_max,
        )
