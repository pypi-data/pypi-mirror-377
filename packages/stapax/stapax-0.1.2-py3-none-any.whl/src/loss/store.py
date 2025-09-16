from typing import Type
import functools as ft

from src.misc.stores import get_cfgs_type, register
from src.loss.types import AbstractLossFunction, BaseLossConfig

RegisteredLossFunctions: dict[
    str, (Type[AbstractLossFunction], Type[BaseLossConfig])
] = {}

register_loss_function = ft.partial(register, registry=RegisteredLossFunctions)
get_loss_function_cfgs_type = ft.partial(
    get_cfgs_type, registry=RegisteredLossFunctions
)
