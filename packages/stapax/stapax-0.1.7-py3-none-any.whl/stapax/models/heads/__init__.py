from typing import List

import jax.random as jr
from jaxtyping import PRNGKeyArray

from .types import Head, HeadBaseConfig

from stapax.misc.stores import import_all_siblings

from .store import RegisteredHeads, get_head_cfgs_type

import_all_siblings(__name__, __file__)
HeadConfig = get_head_cfgs_type()


def get_heads(
    *cfgs: HeadBaseConfig,
    key: PRNGKeyArray,
    input_dim: int,
    output_dim: int,
    **kwargs,
) -> List[Head]:
    keys = jr.split(key, len(cfgs))
    return [
        RegisteredHeads[cfg.name][0](
            input_dim=input_dim,
            output_dim=cfg.output_dim if cfg.output_dim is not None else output_dim,
            cfg=cfg,
            key=key,
            **kwargs,
        )
        for cfg, key in zip(cfgs, keys)
    ]
