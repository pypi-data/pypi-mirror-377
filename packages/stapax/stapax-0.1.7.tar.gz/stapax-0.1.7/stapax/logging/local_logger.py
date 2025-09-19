import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from lightning.pytorch.loggers.logger import Logger
from lightning.pytorch.utilities import rank_zero_only
from matplotlib import pyplot as plt

LOG_PATH = Path("outputs/local_logger")


@dataclass
class LocalExperiment:
    config: dict
    metrics: dict

    def finish(self):
        pass


class LocalLogger(Logger):
    def __init__(self, config: dict) -> None:
        super().__init__()

        print(f"Initializing local logger. Logging to {LOG_PATH}")

        self.experiment = LocalExperiment(config=config, metrics={})
        os.system(f"rm -r {LOG_PATH}")

    @property
    def save_dir(self):
        return str(LOG_PATH)

    @property
    def name(self):
        return "LocalLogger"

    @property
    def version(self):
        return 0

    @rank_zero_only
    def log_hyperparams(self, params):
        pass

    @rank_zero_only
    def log_metrics(self, metrics, step):
        print(f"\n\n{'=' * 10} Step {step} {'=' * 10}")
        for key, value in metrics.items():
            print(f"{step}: {key}: {value}")
        print(f"{'=' * 30}")

    @rank_zero_only
    def log_image(
        self,
        key: str,
        images: list[Any],
        step: Optional[int] = None,
        **kwargs,
    ):
        # The function signature is the same as the wandb logger's, but the step is
        # actually required.
        assert step is not None
        for index, image in enumerate(images):
            path = LOG_PATH / f"{key}/{index:0>2}_{step:0>6}.png"
            path.parent.mkdir(exist_ok=True, parents=True)
            plt.imshow(image)
            plt.savefig(path)
