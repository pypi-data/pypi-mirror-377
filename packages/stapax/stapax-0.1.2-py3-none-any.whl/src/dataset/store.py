from typing import Type
import functools as ft

from src.misc.stores import get_cfgs_type, register
from src.dataset.types import StandardDataset, AbstractDatasetConfig

RegisteredDatasets: dict[str, (Type[StandardDataset], Type[AbstractDatasetConfig])] = {}

register_dataset = ft.partial(register, registry=RegisteredDatasets)
get_dataset_cfgs_type = ft.partial(get_cfgs_type, registry=RegisteredDatasets)
