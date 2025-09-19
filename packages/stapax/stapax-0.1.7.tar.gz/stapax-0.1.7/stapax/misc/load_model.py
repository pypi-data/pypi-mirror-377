import os
from pathlib import Path

import equinox as eqx

from stapax.models import Model


def load_model(
    model: Model, model_state: eqx.nn.State, checkpoint_path: Path
) -> tuple[Model, eqx.nn.State]:
    print(f"Loading model from {checkpoint_path}")
    model = eqx.tree_deserialise_leaves(checkpoint_path, model)
    print(f"Initialized model from {checkpoint_path}")

    # Also load the corresponding state file if it exists
    if checkpoint_path.suffix == ".eqx":
        state_path = checkpoint_path.with_suffix(".eqx.state")
        if os.path.exists(state_path):
            model_state = eqx.tree_deserialise_leaves(state_path, model_state)
            print(f"Loaded model state from {state_path}")
        else:
            print(
                f"Warning: State file {state_path} not found. Using fresh model state."
            )
    else:
        print(
            "Warning: Checkpoint path doesn't end with .eqx, cannot determine state file path."
        )

    return model, model_state
