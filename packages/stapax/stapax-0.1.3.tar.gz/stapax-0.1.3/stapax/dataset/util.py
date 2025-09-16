from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List

import numpy as np


def split(data, bounds: list):
    assert all([b < 1 for b in bounds])
    n = len(data)
    bounds = [0] + [int(n * b) for b in bounds] + [n]
    split_data = [data[bounds[i] : bounds[i + 1]] for i in range(len(bounds) - 1)]
    return tuple(split_data)


def numpy_collate(batch: List[Any]) -> Dict[str, Any]:
    """
    Collate function for PyTorch DataLoader when dataset returns a dataclass
    with fields: input, target, params.

    Args:
        batch: List of dataset items (dataclass instances).

    Returns:
        dict with keys:
        {
            "input": np.ndarray (B, T, F),
            "target": [np.ndarray(B, [T], F), ...],
            "params": { key: np.ndarray(B, [P]) }
        }
    """
    # convert dataclass -> dict
    if is_dataclass(batch[0]):
        batch = [asdict(item) for item in batch]

    inputs = np.stack([item["input"] for item in batch], axis=0)

    # targets: list of heads
    num_heads = len(batch[0]["target"])
    targets = []
    for h in range(num_heads):
        head_data = [item["target"][h] for item in batch]
        targets.append(np.stack(head_data, axis=0))

    dict_to_return = {
        "input": inputs,
        "target": targets,
    }

    # params: dict of stacked arrays
    if batch[0]["params"] is not None:
        dict_to_return["params"] = {}
        for key in batch[0]["params"].keys():
            vals = [item["params"][key] for item in batch]
            # ensure shapes align (e.g. (1,) -> (p,))
            vals = [v if v.ndim > 0 else np.expand_dims(v, 0) for v in vals]
            dict_to_return["params"][key] = np.stack(vals, axis=0)

    return dict_to_return
