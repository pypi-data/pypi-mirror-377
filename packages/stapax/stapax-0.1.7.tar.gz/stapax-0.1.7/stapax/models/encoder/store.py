from typing import Type
import functools as ft

from stapax.misc.stores import get_cfgs_type, register
from stapax.models.encoder.types import Encoder, EncoderBaseConfig

RegisteredEncoders: dict[str, (Type[Encoder], Type[EncoderBaseConfig])] = {}

register_encoder = ft.partial(register, registry=RegisteredEncoders)
get_encoder_cfgs_type = ft.partial(get_cfgs_type, registry=RegisteredEncoders)
