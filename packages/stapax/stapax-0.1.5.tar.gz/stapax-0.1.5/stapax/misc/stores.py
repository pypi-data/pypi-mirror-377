import importlib
import pkgutil
import pathlib
from typing import Any, Callable, Dict, Type, TypeVar, Union, get_args, Tuple

M = TypeVar("M")  # Model type
C = TypeVar("C")  # Config type


Registry = Dict[str, Tuple[Type[M], Type[C]]]


def import_all_siblings(pkg: str, file: str):
    pkg_path = pathlib.Path(file).parent
    for _, modname, _ in pkgutil.iter_modules([str(pkg_path)]):
        importlib.import_module(f"{pkg}.{modname}")


def register(registry: Registry[M, C], cfg: Type[C]) -> Callable[[Type[M]], Type[M]]:
    """
    Decorator that registers a model class with its config into the given registry.
    Assumes the config has a field `name: Literal["..."]`.
    """

    def decorator(model_cls: Type[M]) -> Type[M]:
        # extract name from cfg annotation
        names = get_args(cfg.__annotations__.get("name"))
        for name in names:
            registry[name] = (model_cls, cfg)
        return model_cls

    return decorator


def get_cfgs_type(registry: Registry[M, C]) -> Type[Union[C, Any]]:
    """
    Returns a Union of all registered config types.
    """
    cfg_types = [cfg for _, cfg in registry.values()]
    if not cfg_types:
        raise ValueError("No configs registered")
    return Union[tuple(cfg_types)]
