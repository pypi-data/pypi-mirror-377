from dataclasses import dataclass
from typing import List, Literal

import equinox as eqx
import jax
import jax.numpy as jnp
import jax.random as jr
from jaxtyping import PRNGKeyArray

from stapax.models.sequence_mixer import SequenceMixerConfig
from stapax.models.sequence_mixer.types import SequenceMixer

from .types import Encoder, EncoderBaseConfig
from .store import register_encoder


class GLU(eqx.Module):
    w1: eqx.nn.Linear
    w2: eqx.nn.Linear

    def __init__(self, input_dim, output_dim, key):
        w1_key, w2_key = jr.split(key, 2)
        self.w1 = eqx.nn.Linear(input_dim, output_dim, use_bias=True, key=w1_key)
        self.w2 = eqx.nn.Linear(input_dim, output_dim, use_bias=True, key=w2_key)

    def __call__(self, x):
        return self.w1(x) * jax.nn.sigmoid(self.w2(x))


class LinossEncoderBlock(eqx.Module):
    norm: eqx.nn.BatchNorm
    sequence_mixer: SequenceMixer
    glu: GLU
    drop: eqx.nn.Dropout

    def __init__(
        self,
        H,
        drop_rate,
        *,
        input_dtype: jnp.dtype,
        sequence_mixer: SequenceMixer,
        key,
    ):
        sequence_mixerkey, glukey = jr.split(key, 2)
        # self.norm = eqx.nn.BatchNorm(
        #     input_size=H,
        #     axis_name="batch",
        #     channelwise_affine=False,
        #     mode="ema",
        #     dtype=input_dtype,
        # )
        self.norm = eqx.nn.LayerNorm(H)
        self.sequence_mixer = sequence_mixer
        self.glu = GLU(H, H, key=glukey)
        self.drop = eqx.nn.Dropout(p=drop_rate)

    def __call__(self, x, state, *, key):
        """Compute LinOSS block."""
        dropkey1, dropkey2 = jr.split(key, 2)
        skip = x
        x = self.sequence_mixer(x)
        x, state = jax.vmap(self.norm)(x, state)
        # x = x.T
        x = self.drop(jax.nn.gelu(x), key=dropkey1)  # 12*12=144
        x = jax.vmap(self.glu)(x)
        x = self.drop(x, key=dropkey2)
        x = skip + x

        return x, state


@dataclass
class LinossEncoderConfig(EncoderBaseConfig):
    name: Literal["linoss_encoder"]
    num_blocks: int
    hidden_dim: int
    sequence_mixer: SequenceMixerConfig
    use_embedding: bool = False
    pass_through: bool = False
    dropout_rate: float = 0.05


@register_encoder(cfg=LinossEncoderConfig)
class LinossEncoder(Encoder):
    linear_encoder: eqx.nn.Linear
    blocks: List[LinossEncoderBlock]
    embedding: eqx.nn.Embedding | None
    hidden_dim: int
    use_embedding: bool
    pass_through: bool

    def __init__(
        self,
        input_dim: int,
        cfg: LinossEncoderConfig,
        input_dtype: jnp.dtype,
        key: PRNGKeyArray,
        sequence_mixer_cls: SequenceMixer,
        num_embeddings: int | None = None,
        **kwargs,
    ):
        self.hidden_dim = cfg.hidden_dim
        self.use_embedding = cfg.use_embedding
        self.pass_through = cfg.pass_through

        key, embedding_key = jr.split(key, 2)
        if cfg.use_embedding:
            self.embedding = eqx.nn.Embedding(
                num_embeddings=num_embeddings,
                embedding_size=cfg.hidden_dim,
                key=embedding_key,
            )
        else:
            self.embedding = None

        key, linear_encoder_key, *block_keys = jr.split(key, cfg.num_blocks + 2)
        key, *mixer_keys = jr.split(key, cfg.num_blocks + 1)
        self.linear_encoder = eqx.nn.Linear(
            input_dim, cfg.hidden_dim, key=linear_encoder_key, dtype=input_dtype
        )
        self.blocks = [
            LinossEncoderBlock(
                cfg.hidden_dim,
                input_dtype=input_dtype,
                key=b_key,
                sequence_mixer=sequence_mixer_cls(
                    cfg=cfg.sequence_mixer,
                    input_dim=cfg.hidden_dim,
                    input_dtype=input_dtype,
                    key=m_key,
                    **kwargs,
                ),
                drop_rate=cfg.dropout_rate,
            )
            for (m_key, b_key) in zip(mixer_keys, block_keys)
        ]

    def __call__(self, x, state, key):
        """ """
        dropout_keys = jr.split(key, len(self.blocks))
        if self.use_embedding:
            y = jax.vmap(self.embedding)(x[:, 0].astype(jnp.int32))
        else:
            y = jax.vmap(self.linear_encoder)(x)  # 6

        intermediate_results = [y]
        for i, (block, d_key) in enumerate(zip(self.blocks, dropout_keys)):
            # x shape is (timesteps, hidden_dim)
            y, state = block(y, state, key=d_key)
            intermediate_results.append(y)

        if self.pass_through:
            y = jnp.concatenate(intermediate_results, axis=1)

        return y, state

    @property
    def output_dim(self) -> int:
        if self.pass_through:
            return self.hidden_dim * (len(self.blocks) + 1)
        else:
            return self.hidden_dim
