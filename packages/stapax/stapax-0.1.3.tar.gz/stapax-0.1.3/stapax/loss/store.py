from typing import Type
import functools as ft

from stapax.misc.stores import get_cfgs_type, register
from stapax.loss.types import AbstractLossFunction, BaseLossConfig

RegisteredLossFunctions: dict[
    str, (Type[AbstractLossFunction], Type[BaseLossConfig])
] = {}

register_loss_function = ft.partial(register, registry=RegisteredLossFunctions)
get_loss_function_cfgs_type = ft.partial(
    get_cfgs_type, registry=RegisteredLossFunctions
)
