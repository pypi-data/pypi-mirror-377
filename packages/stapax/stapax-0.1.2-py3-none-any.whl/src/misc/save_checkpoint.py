import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import equinox as eqx
from pytorch_lightning import Callback, LightningModule
from pytorch_lightning.trainer import Trainer

from src.misc.step_tracker import StepTracker


@dataclass
class CheckpointCfg:
    metric: str | None = None
    mode: Literal["min", "max"] = "max"
    metric_top_k: int = 20
    step_top_k: int = 10
    every_n_steps: int | None = None
    warmup_steps: int | None = 1


class CheckpointManager(Callback):
    def __init__(self, output_dir: Path, cfg: CheckpointCfg, step_tracker: StepTracker):
        self.output_dir = output_dir / "checkpoints"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cfg = cfg
        self.step_tracker = step_tracker

        # Separate tracking for metric-based and step-based checkpoints
        self.metric_checkpoints: dict[float, tuple[Path, Path]] = {}
        self.step_checkpoints: dict[int, tuple[Path, Path]] = {}
        self.best_metric: float | None = None

        # Save every 1000 steps if no metric is provided.
        if cfg.metric is None and cfg.every_n_steps is None:
            self.cfg.every_n_steps = 1000

    def on_validation_epoch_end(self, trainer: Trainer, pl_module: LightningModule):
        if self._should_skip_warmup(trainer):
            return

        # Handle metric-based saving
        if self.cfg.metric is not None:
            self._save_by_metric(trainer)

        # Handle step-based saving
        if self.cfg.every_n_steps is not None:
            self._save_by_steps(trainer)

    def _should_skip_warmup(self, trainer: Trainer) -> bool:
        current_step = self.step_tracker.get_step()
        if self.cfg.warmup_steps is not None and current_step < self.cfg.warmup_steps:
            print(f"Skipping checkpoint saving during warmup: step {current_step}")
            return True
        return False

    def _save_by_metric(self, trainer: Trainer):
        try:
            score = trainer.logged_metrics[self.cfg.metric].item()
            if self._is_better_metric(score):
                self.best_metric = score
                self._save_checkpoint(trainer, score=score, checkpoint_type="metric")
        except KeyError:
            print(
                f"Metric '{self.cfg.metric}' not found in logged metrics, saving every {self.cfg.every_n_steps or '1000'} steps"
            )
            if self.cfg.every_n_steps is None:
                self.cfg.every_n_steps = 1000

    def _save_by_steps(self, trainer: Trainer):
        current_step = self.step_tracker.get_step()
        if current_step % self.cfg.every_n_steps == 0:
            self._save_checkpoint(trainer, checkpoint_type="step")

    def _is_better_metric(self, score: float) -> bool:
        if self.best_metric is None:
            return True
        return (
            score > self.best_metric
            if self.cfg.mode == "max"
            else score < self.best_metric
        )

    def _save_checkpoint(
        self,
        trainer: Trainer,
        score: float | None = None,
        checkpoint_type: str = "step",
    ):
        self._cleanup_old_checkpoints(checkpoint_type)

        model_path, state_path = self._get_checkpoint_paths(trainer, score)

        # Save model and state
        eqx.tree_serialise_leaves(model_path, trainer.lightning_module.model)
        eqx.tree_serialise_leaves(state_path, trainer.lightning_module.model_state)

        current_step = self.step_tracker.get_step()
        # Track checkpoint
        if checkpoint_type == "metric" and score is not None:
            self.metric_checkpoints[score] = (model_path, state_path)
            print(f"Saved metric checkpoint (score={score}) at step {current_step}")
        else:
            self.step_checkpoints[current_step] = (model_path, state_path)
            print(f"Saved step checkpoint at step {current_step}")

    def _get_checkpoint_paths(
        self, trainer: Trainer, score: float | None = None
    ) -> tuple[Path, Path]:
        suffix = f"_metric_{score}" if score is not None else ""
        current_step = self.step_tracker.get_step()
        base_name = f"checkpoint_step_{current_step}{suffix}"
        return (
            self.output_dir / f"{base_name}.eqx",
            self.output_dir / f"{base_name}.eqx.state",
        )

    def _cleanup_old_checkpoints(self, checkpoint_type: str):
        if checkpoint_type == "metric":
            self._remove_excess_checkpoints(
                self.metric_checkpoints, self.cfg.metric_top_k, use_mode=True
            )
        else:
            self._remove_excess_checkpoints(
                self.step_checkpoints, self.cfg.step_top_k, use_mode=False
            )

    def _remove_excess_checkpoints(
        self, checkpoint_dict: dict, top_k: int, use_mode: bool
    ):
        if len(checkpoint_dict) >= top_k:
            # Sort checkpoints - for metrics use mode, for steps use ascending order
            reverse_sort = self.cfg.mode == "max" if use_mode else False
            sorted_items = sorted(
                checkpoint_dict.items(), key=lambda x: x[0], reverse=reverse_sort
            )

            # Remove the worst/oldest checkpoint
            key_to_remove, (model_path, state_path) = sorted_items[-1]
            self._delete_checkpoint_files(model_path, state_path)
            del checkpoint_dict[key_to_remove]

    def _delete_checkpoint_files(self, model_path: Path, state_path: Path):
        for path in [model_path, state_path]:
            if path.exists():
                os.remove(path)

    def get_best_checkpoint(self) -> tuple[Path, Path, float]:
        """Returns (model_path, state_path, best_metric)"""
        if self.best_metric is None or self.best_metric not in self.metric_checkpoints:
            raise ValueError("No best metric checkpoint available")
        model_path, state_path = self.metric_checkpoints[self.best_metric]
        return model_path, state_path, self.best_metric
