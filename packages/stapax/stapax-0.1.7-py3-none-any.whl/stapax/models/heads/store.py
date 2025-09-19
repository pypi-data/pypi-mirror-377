from typing import Type
import functools as ft

from stapax.misc.stores import get_cfgs_type, register
from stapax.models.heads.types import Head, HeadBaseConfig

RegisteredHeads: dict[str, (Type[Head], Type[HeadBaseConfig])] = {}

register_head = ft.partial(register, registry=RegisteredHeads)
get_head_cfgs_type = ft.partial(get_cfgs_type, registry=RegisteredHeads)
