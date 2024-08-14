"""Root context models."""

from functools import partial
from pathlib import Path
from typing import Annotated, ClassVar, Unpack

from pydantic import AfterValidator, BaseModel, ConfigDict

from boilercv_pipeline.contexts import ContextsBaseModel
from boilercv_pipeline.contexts.types import PluginConfigDict
from boilercv_pipeline.root_contexts.types import (
    RootConfigDict,
    RootContexts,
    RootContextsValidationInfo,
    RootCtx,
    RootSettings,
)


def make_absolute_directory(
    path: Path, info: RootContextsValidationInfo, key: str
) -> Path:
    """Make directory absolute and make the directory."""
    if not path.is_absolute() and (root := info.context.get("root", {}).get(key)):
        path = root / path
        path.mkdir(exist_ok=True, parents=True)
    return path


def make_absolute_file(path: Path, info: RootContextsValidationInfo, key: str) -> Path:
    """Make file path absolute and touch the file."""
    if not path.is_absolute() and (root := info.context.get("root", {}).get(key)):
        path = root / path
        path.parent.mkdir(exist_ok=True, parents=True)
        path.touch()
    return path


DataDir = Annotated[Path, AfterValidator(partial(make_absolute_directory, key="data"))]
"""Data directory path made upon validation."""
DataFile = Annotated[Path, AfterValidator(partial(make_absolute_file, key="data"))]
"""Data file path made upon validation."""
DocsDir = Annotated[Path, AfterValidator(partial(make_absolute_directory, key="docs"))]
"""Docs directory path made upon validation."""
DocsFile = Annotated[Path, AfterValidator(partial(make_absolute_file, key="docs"))]
"""Docs file path made upon validation."""


class Outs(ContextsBaseModel):
    """Outs."""

    file: DataFile = Path(__file__).relative_to(Path.cwd())
    folder: DataDir = Path(__file__).parent.relative_to(Path.cwd())


def get_config(
    *, data: Path | None = None, docs: Path | None = None, **kwds: Unpack[ConfigDict]
) -> PluginConfigDict[RootSettings]:
    """Pydantic model config with root context."""
    cwd = Path.cwd()
    return {
        **RootConfigDict(
            plugin_settings=RootSettings(
                contexts=RootContexts(
                    root=RootCtx(data=data or cwd / "data", docs=docs or cwd / "docs")
                )
            )
        ),
        "validate_default": True,
        **kwds,
    }


class Params(BaseModel):  # noqa: D101
    model_config: ClassVar[RootConfigDict] = get_config()  # pyright: ignore[reportIncompatibleVariableOverride]
