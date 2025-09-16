from typing import Tuple


from stapax.misc.stores import import_all_siblings
from stapax.models.sequence_mixer.types import SequenceMixer

from .store import get_sequence_mixer_cfgs_type, RegisteredSequenceMixers

import_all_siblings(__name__, __file__)
SequenceMixerConfig = get_sequence_mixer_cfgs_type()


def get_sequence_mixer_cls(
    cfg: SequenceMixerConfig,
    # input_dim: int,
    # key: PRNGKeyArray,
    **kwargs,
) -> Tuple[SequenceMixer, dict[str, bool]]:
    sequence_mixer = RegisteredSequenceMixers[cfg.name][0]

    # TODO: Philipp removed this because he is a noob. Should probably be restored at some point
    # filter_spec = jax.tree_util.tree_map(
    #    sequence_mixer.filter_spec_lambda(), sequence_mixer
    # )

    return sequence_mixer, None
