from typing import Type
import functools as ft

from stapax.misc.stores import get_cfgs_type, register
from stapax.models.sequence_mixer.types import SequenceMixer, SequenceMixerBaseConfig

RegisteredSequenceMixers: dict[
    str, (Type[SequenceMixer], Type[SequenceMixerBaseConfig])
] = {}


register_sequence_mixer = ft.partial(register, registry=RegisteredSequenceMixers)
get_sequence_mixer_cfgs_type = ft.partial(
    get_cfgs_type, registry=RegisteredSequenceMixers
)
