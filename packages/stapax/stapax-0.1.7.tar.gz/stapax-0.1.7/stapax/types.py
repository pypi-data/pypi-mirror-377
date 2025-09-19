from typing import TypedDict

from stapax.dataset.types import BatchedParams, ModelOutput


class JaxLightningStepOutput(TypedDict):
    outputs: ModelOutput
    params: BatchedParams | None
