from typing import List, Tuple

from lightning import Callback

from stapax.metric.metrics import RegisteredMetrics
from stapax.models.model import Model

__all__ = ["RegisteredMetrics"]


def get_metrics_for_heads(model: Model) -> list[Callback]:
    callbacks = []
    names = [head.name for head in model.heads]

    # if there are multiple heads of the same type add _1, _2, etc.
    for name in names:
        if names.count(name) > 1:
            p = 0
            for i in range(names.count(name)):
                p = names.index(name, p)
                names[p] = f"{name}_{i}"

    # add metrics for each head
    metrics_dict: dict[str, List[Tuple[str, int]]] = {}
    for i, (head, name) in enumerate(zip(model.heads, names)):
        metrics = head.metrics
        for metric in metrics:
            if metric not in metrics_dict:
                metrics_dict[metric] = []
            metrics_dict[metric].append((name, i))

    for metric_name, heads in metrics_dict.items():
        callbacks.append(RegisteredMetrics[metric_name](heads))
    return callbacks
