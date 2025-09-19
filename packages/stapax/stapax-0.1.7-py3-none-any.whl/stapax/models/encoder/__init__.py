from typing import Tuple

import jax
import jax.numpy as jnp
from jaxtyping import PRNGKeyArray

from stapax.misc.stores import import_all_siblings
from stapax.models.encoder.types import Encoder
from stapax.models.sequence_mixer.types import SequenceMixer

from stapax.models.encoder.store import RegisteredEncoders, get_encoder_cfgs_type

import_all_siblings(__name__, __file__)
EncoderConfig = get_encoder_cfgs_type()


def get_encoder(
    cfg: EncoderConfig,
    key: PRNGKeyArray,
    input_dim: int,
    input_dtype: jnp.dtype,
    sequence_mixer_cls: SequenceMixer | None = None,
    num_embeddings: int | None = None,
    **kwargs,
) -> Tuple[Encoder, dict[str, bool]]:
    encoder_cls, _ = RegisteredEncoders[cfg.name]
    encoder = encoder_cls(
        input_dim=input_dim,
        cfg=cfg,
        input_dtype=input_dtype,
        key=key,
        sequence_mixer_cls=sequence_mixer_cls,
        num_embeddings=num_embeddings,
        **kwargs,
    )
    filter_spec = jax.tree_util.tree_map(encoder.filter_spec_lambda(), encoder)
    return encoder, filter_spec
