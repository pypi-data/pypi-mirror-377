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


def make_runtime_registry_hook(
    base_type: Type[C], registry: Registry[M, C]
) -> Dict[Type[Any], Callable[[Any], Any]]:
    """Create a dacite type hook that dispatches to the correct config class at runtime.

    This lets dataclass loading remain dynamic: as new cfg classes are registered,
    the hook will resolve them by their `name` field and instantiate that class.
    """

    def _hook(data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        name = data.get("name")
        if name is None:
            return data
        try:
            _, cfg_cls = registry[name]
        except KeyError as e:
            raise ValueError(
                f"Unknown config name '{name}' for {base_type.__name__}"
            ) from e
        # Instantiate directly; nested fields will be handled by outer dacite call
        return cfg_cls(**data)

    return {base_type: _hook}


def build_registry_hooks() -> Dict[Type[Any], Callable[[Any], Any]]:
    """Build dacite type hooks for all known registries.

    Keeps import and wiring logic in one place so callers (e.g. config loading)
    can stay concise.
    """

    hooks: Dict[Type[Any], Callable[[Any], Any]] = {}

    # Import locally to avoid import cycles on module import.
    try:
        from stapax.models.sequence_mixer import SequenceMixerConfig  # type: ignore
        from stapax.models.sequence_mixer.store import RegisteredSequenceMixers  # type: ignore

        hooks.update(
            make_runtime_registry_hook(SequenceMixerConfig, RegisteredSequenceMixers)
        )
    except Exception:
        pass

    try:
        from stapax.models.encoder import EncoderConfig  # type: ignore
        from stapax.models.encoder.store import RegisteredEncoders  # type: ignore

        hooks.update(make_runtime_registry_hook(EncoderConfig, RegisteredEncoders))
    except Exception:
        pass

    try:
        from stapax.models.heads import HeadConfig  # type: ignore
        from stapax.models.heads.store import RegisteredHeads  # type: ignore

        hooks.update(make_runtime_registry_hook(HeadConfig, RegisteredHeads))
    except Exception:
        pass

    try:
        from stapax.loss import LossFunctionConfig  # type: ignore
        from stapax.loss.store import RegisteredLossFunctions  # type: ignore

        hooks.update(
            make_runtime_registry_hook(LossFunctionConfig, RegisteredLossFunctions)
        )
    except Exception:
        pass

    try:
        from stapax.dataset import DatasetConfig  # type: ignore
        from stapax.dataset.store import RegisteredDatasets  # type: ignore

        hooks.update(make_runtime_registry_hook(DatasetConfig, RegisteredDatasets))
    except Exception:
        pass

    return hooks
