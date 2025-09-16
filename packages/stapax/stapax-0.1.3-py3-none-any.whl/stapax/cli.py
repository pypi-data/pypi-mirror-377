#!/usr/bin/env python3
"""
Command-line interface for stapax.
This script handles config path resolution for both development and installed package scenarios.
"""

import hydra
from omegaconf import DictConfig

from .config import get_config_dir
from .main import main as main_func


def cli_main():
    """CLI entry point that sets up the correct config path."""
    config_dir = get_config_dir()

    # Override the hydra decorator with the correct config path
    @hydra.main(
        version_base=None,
        config_name="main",
        config_path=str(config_dir),
    )
    def wrapped_main(cfg_dict: DictConfig) -> float | None:
        return main_func(cfg_dict)

    # Run the wrapped main function
    wrapped_main()


if __name__ == "__main__":
    cli_main()
