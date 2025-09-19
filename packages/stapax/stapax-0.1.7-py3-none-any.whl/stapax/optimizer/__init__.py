import equinox as eqx
import optax

from stapax.config import TrainCfg
from stapax.misc.learning_rate import get_learning_rate_schedule
from stapax.models.model import Model


def get_optimizer(config: TrainCfg, model: Model):
    lr_schedule = get_learning_rate_schedule(config.lr)
    optimizer = None

    if config.weight_decay is not None:
        optimizer = optax.adamw(
            lr_schedule,
            weight_decay=config.weight_decay,
            b1=0.9,
            b2=0.98,
        )
    else:
        optimizer = optax.adam(lr_schedule, b1=0.9, b2=0.98)

    if config.clip_grad_global_norm is not None:
        optimizer = optax.chain(
            optax.clip_by_global_norm(config.clip_grad_global_norm),
            optimizer,
        )
    opt_state = optimizer.init(eqx.filter(model, eqx.is_inexact_array))

    return optimizer, opt_state, lr_schedule
