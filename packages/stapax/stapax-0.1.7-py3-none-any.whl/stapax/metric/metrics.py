import functools as ft

import jax
import jax.numpy as jnp
from jaxtyping import Scalar

from stapax.dataset.types import UnbatchedTarget
from stapax.metric.types import CustomMetric, Metric

RegisteredMetrics: dict[str, CustomMetric] = {}


def metric(name: str = None, prog_bar: bool = False, jit: bool = False):
    """Decorator to register a metric function."""

    def decorator(func: Metric) -> Metric:
        metric_name = name or func.__name__

        RegisteredMetrics[metric_name] = ft.partial(
            CustomMetric,
            metric=jax.jit(func) if jit else func,
            metric_name=metric_name,
            prog_bar=prog_bar,
        )

        return func

    return decorator


@metric()
def mse(target: UnbatchedTarget, pred: UnbatchedTarget, **kwargs) -> Scalar:
    return jnp.mean((pred - target) ** 2)


@metric()
def rel_mse(target: UnbatchedTarget, pred: UnbatchedTarget, **kwargs) -> Scalar:
    return jnp.mean((pred - target) ** 2) / jnp.mean(target**2)


@metric()
def l1_loss(target: UnbatchedTarget, pred: UnbatchedTarget, **kwargs) -> Scalar:
    return jnp.mean(jnp.abs(pred - target))


@metric()
def accuracy(target: UnbatchedTarget, pred: UnbatchedTarget, **kwargs) -> Scalar:
    return jnp.mean(target == pred)


# TODO: actually, the pred and target seem to be batched....
@metric()
def masked_accuracy(target: UnbatchedTarget, pred: UnbatchedTarget, **kwargs) -> Scalar:
    # y has shape T, y_hat has shape T x C.

    # TODO: the average should be taken over all samples in the end, not just one batch. If we do it this way, we should do a moving average.

    # there are num_tokens_to_copy * batch_size valid tokens (can check by printing jnp.sum(mask))
    mask = target != -100

    # mask out the tokens with -100
    target = target[mask]
    pred = pred[mask]

    # compute the accuracy over the valid tokens
    # accuracy = jnp.mean(target == jnp.argmax(pred, axis=-1))

    return accuracy(target, jnp.argmax(pred, axis=-1))


# TODO: this is a batched target
@metric()
def one_hot_accuracy(
    target: UnbatchedTarget, pred: UnbatchedTarget, **kwargs
) -> Scalar:
    return accuracy(jnp.argmax(target, axis=-1), jnp.argmax(pred, axis=-1))


@metric()
def false_positive_rate(
    target: UnbatchedTarget, pred: UnbatchedTarget, **kwargs
) -> Scalar:
    return jnp.mean(target == 0 & pred == 1)


@metric()
def false_negative_rate(
    target: UnbatchedTarget, pred: UnbatchedTarget, **kwargs
) -> Scalar:
    return jnp.mean(target == 1 & pred == 0)


@metric()
def true_positive_rate(
    target: UnbatchedTarget, pred: UnbatchedTarget, **kwargs
) -> Scalar:
    return jnp.mean(target == 1 & pred == 1)


@metric()
def true_negative_rate(
    target: UnbatchedTarget, pred: UnbatchedTarget, **kwargs
) -> Scalar:
    return jnp.mean(target == 0 & pred == 0)


@metric()
def f1_score(target: UnbatchedTarget, pred: UnbatchedTarget, **kwargs) -> Scalar:
    tp = true_positive_rate(target, pred)
    fp = false_positive_rate(target, pred)
    fn = false_negative_rate(target, pred)
    return 2 * tp / (2 * tp + fp + fn)


@metric()
def l1_magnitude(target: UnbatchedTarget, pred: UnbatchedTarget, **kwargs) -> Scalar:
    return jnp.mean(jnp.abs(pred))
