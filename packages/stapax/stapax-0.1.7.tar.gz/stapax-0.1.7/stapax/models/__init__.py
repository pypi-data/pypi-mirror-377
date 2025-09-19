from typing import Tuple
import logging

import equinox as eqx
import jax
import jax.numpy as jnp
from jaxtyping import PRNGKeyArray

from stapax.models.encoder import get_encoder
from stapax.models.heads import get_heads
from stapax.models.model import Model, ModelConfig
from stapax.models.sequence_mixer import get_sequence_mixer_cls


logger = logging.getLogger(__name__)


def get_model(
    cfg: ModelConfig,
    input_feature_dim: int,
    target_feature_dim: int,
    input_dtype: jnp.dtype,
    key: PRNGKeyArray,
    num_embeddings: int | None = None,
    **kwargs,
) -> Tuple[Model, eqx.nn.State, dict[str, bool], int]:
    """ """
    filter_spec = {}
    if (
        hasattr(cfg.encoder, "sequence_mixer")
        and cfg.encoder.sequence_mixer is not None
    ):
        sequence_mixer_cls, sequence_mixer_filter_spec = get_sequence_mixer_cls(
            cfg=cfg.encoder.sequence_mixer,
            # input_dim=cfg.encoder.hidden_dim,
            # key=key,
            # input_dtype=input_dtype,
            # **kwargs,
        )
    else:
        sequence_mixer_cls = None
        filter_spec["sequence_mixer"] = False

    encoder, encoder_filter_spec = get_encoder(
        cfg=cfg.encoder,
        key=key,
        input_dim=input_feature_dim,
        input_dtype=input_dtype,
        sequence_mixer_cls=sequence_mixer_cls,
        num_embeddings=num_embeddings,
        **kwargs,
    )

    heads = get_heads(
        *cfg.heads,
        key=key,
        input_dim=encoder.output_dim,
        output_dim=target_feature_dim,
        **kwargs,
    )

    model = Model(encoder, heads)
    filter_spec = jax.tree_util.tree_map(model.filter_spec_lambda(), model)

    param_count = sum(
        x.size for x in jax.tree.leaves(eqx.filter(model, eqx.is_inexact_array))
    )

    logger.info(f"Created model with param count: {param_count}")

    return model, eqx.nn.State(model), filter_spec, param_count
