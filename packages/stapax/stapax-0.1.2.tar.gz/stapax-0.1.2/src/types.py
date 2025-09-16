from typing import TypedDict

from src.dataset.types import BatchedParams, ModelOutput


class JaxLightningStepOutput(TypedDict):
    outputs: ModelOutput
    params: BatchedParams | None
