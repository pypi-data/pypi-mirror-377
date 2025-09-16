from functools import partial
from typing import List

from jaxtyping import Scalar

from stapax.dataset.types import HeadOutput
from stapax.loss.types import LossFunction, BaseLossConfig


from stapax.loss.store import RegisteredLossFunctions


def get_loss_fns(*head_cfgs: "BaseLossConfig") -> List[LossFunction]:
    loss_fns: List[LossFunction] = []
    for head_cfg in head_cfgs:
        if len(head_cfg.loss_fns) == 0:
            raise ValueError("Must have at least one loss function for each head")

        head_loss_fns = []
        for loss_fn_cfg in head_cfg.loss_fns:
            head_loss_fns.append(
                partial(RegisteredLossFunctions[loss_fn_cfg.name][0](), loss_fn_cfg)
            )

        def head_loss_fn(y: HeadOutput, head_output: HeadOutput) -> Scalar:
            loss = 0.0
            for loss_fn in head_loss_fns:
                loss += loss_fn(y, head_output)

            return loss

        loss_fns.append(head_loss_fn)

    return loss_fns
