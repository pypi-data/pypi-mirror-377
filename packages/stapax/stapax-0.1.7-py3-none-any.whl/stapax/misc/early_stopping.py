from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import EarlyStopping


class EarlyStoppingWithWarmup(EarlyStopping):
    """
    EarlyStopping, except don't watch the first `warmup_steps` steps.

    if warmup_steps is None, this is the same as EarlyStopping.
    """

    warmup_steps: int | None = None

    def __init__(self, warmup_steps: int | None = None, **kwargs):
        super().__init__(**kwargs)
        self.warmup_steps = warmup_steps

    def on_validation_end(self, trainer: Trainer, pl_module):
        if (
            self._check_on_train_epoch_end
            or self._should_skip_check(trainer)
            or (
                self.warmup_steps is not None
                and trainer.global_step < self.warmup_steps
            )
        ):
            return
        self._run_early_stopping_check(trainer)
