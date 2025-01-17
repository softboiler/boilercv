"""Module names."""

from importlib.machinery import ModuleSpec
from pathlib import Path
from types import ModuleType


def get_package_dir(package: ModuleType) -> Path:
    """Get the directory of a package given the top-level module."""
    return Path(package.__spec__.submodule_search_locations[0])  # type: ignore


def get_module_name(module: ModuleType | ModuleSpec | Path | str) -> str:
    """Get an unqualified module name.

    Example: `get_module_name(__spec__ or __file__)`.
    """
    if isinstance(module, ModuleType | ModuleSpec):
        return get_qualified_module_name(module).split(".")[-1]
    path = Path(module)
    return path.parent.name if path.stem in ("__init__", "__main__") else path.stem


def get_qualified_module_name(module: ModuleType | ModuleSpec) -> str:  # type: ignore
    """Get a fully-qualified module name.

    Example: `get_module_name(__spec__ or __file__)`.
    """
    if isinstance(module, ModuleType):
        module: ModuleSpec = module.__spec__  # type: ignore
    return module.name
