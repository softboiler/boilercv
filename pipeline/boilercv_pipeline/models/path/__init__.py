"""Path models."""

from __future__ import annotations

from collections.abc import Mapping
from functools import partial
from pathlib import Path
from re import search
from typing import Annotated as Ann
from typing import ClassVar, Self, TypeAlias

from boilercore.paths import ISOLIKE, dt_fromisolike
from cappa.arg import Arg
from context_models import ContextStore
from context_models.serializers import ContextWrapSerializer
from context_models.types import Context, ContextPluginSettings, Data, PluginConfigDict
from context_models.validators import ContextAfterValidator
from pydantic import (
    DirectoryPath,
    FilePath,
    SerializerFunctionWrapHandler,
    WrapSerializer,
    model_validator,
)

from boilercv_pipeline.models.contexts import (
    BOILERCV_PIPELINE,
    DVC,
    BoilercvPipelineContext,
    BoilercvPipelineContexts,
    DvcContext,
    Roots,
)
from boilercv_pipeline.models.contexts.types import (
    BoilercvPipelineConfigDict,
    BoilercvPipelineSerializationInfo,
    BoilercvPipelineValidationInfo,
    Kind,
)
from boilercv_pipeline.models.path.types import Key


def get_times(directory: Path, pattern: str) -> list[str]:
    """Get timestamps from a pattern-filtered directory."""
    return [
        dt_fromisolike(match).isoformat()
        for path in directory.iterdir()
        if (match := ISOLIKE.search(path.stem)) and search(pattern, path.stem)
    ]


def get_time(path: Path) -> str:
    """Get timestamp from a path."""
    return match.group() if (match := ISOLIKE.search(path.stem)) else ""


def get_boilercv_pipeline_context(
    roots: Roots | None = None,
    kinds_from: BoilercvPipelineContextStore | None = None,
    track_kinds: bool = False,
    sync_dvc: bool = False,
) -> BoilercvPipelineContexts:
    """Context for {mod}`~boilercv_pipeline`."""
    ctx_from: BoilercvPipelineContexts = getattr(
        kinds_from,
        "context",
        BoilercvPipelineContexts(boilercv_pipeline=BoilercvPipelineContext()),
    )
    return BoilercvPipelineContexts(
        boilercv_pipeline=BoilercvPipelineContext(
            roots=roots or Roots(),
            kinds=ctx_from[BOILERCV_PIPELINE].kinds,
            track_kinds=track_kinds,
        ),
        **({DVC: DvcContext()} if sync_dvc else {}),
    )


def get_boilercv_pipeline_config(
    roots: Roots | None = None,
    kinds_from: BoilercvPipelineContextStore | None = None,
    track_kinds: bool = False,
    dvc: bool = False,
) -> BoilercvPipelineConfigDict:
    """Model config for {mod}`~boilercv_pipeline`."""
    return PluginConfigDict(
        validate_default=True,
        plugin_settings=ContextPluginSettings(
            context=get_boilercv_pipeline_context(
                roots=roots,
                kinds_from=kinds_from,
                track_kinds=track_kinds,
                sync_dvc=dvc,
            )
        ),
    )


HiddenContext = Ann[BoilercvPipelineContexts, Arg(hidden=True)]
"""Pipeline context as a hidden argument."""


class BoilercvPipelineContextStore(ContextStore):
    """Context model for {mod}`~boilercv_pipeline`."""

    model_config: ClassVar[BoilercvPipelineConfigDict] = get_boilercv_pipeline_config()  # pyright: ignore[reportIncompatibleVariableOverride]
    context: HiddenContext = BoilercvPipelineContexts(  # pyright: ignore[reportIncompatibleVariableOverride]
        boilercv_pipeline=BoilercvPipelineContext()
    )

    @classmethod
    def context_get(
        cls,
        data: Data,
        context: Context | None = None,
        context_base: Context | None = None,
    ) -> Context:
        """Get context from data."""
        return BoilercvPipelineContexts({  # pyright: ignore[reportArgumentType]
            k: (
                {BOILERCV_PIPELINE: BoilercvPipelineContext}[k].model_validate(v)
                if isinstance(v, Mapping)
                else v
            )
            for k, v in super().context_get(data, context, context_base).items()
        })

    @model_validator(mode="after")
    def unset_kinds(self) -> Self:
        """Unset kinds to avoid re-checking them."""
        self.context[BOILERCV_PIPELINE].kinds = {}
        return self


make_path_args: dict[tuple[Key, bool], Kind] = {
    ("data", False): "DataDir",
    ("data", True): "DataFile",
    ("docs", False): "DocsDir",
    ("docs", True): "DocsFile",
}
"""{func}`~boilercv_pipeline.models.types.runtime.make_path` args and their kinds."""


def make_path(
    path: Path, info: BoilercvPipelineValidationInfo, key: Key, file: bool
) -> Path:
    """Check path kind and make a directory and its parents or a file's parents."""
    ctx = info.context[BOILERCV_PIPELINE]
    root = getattr(ctx.roots, key, None)
    kind = make_path_args[key, file]
    if root:
        path = (root.resolve() / path) if path.is_absolute() else root / path
    if ctx.track_kinds:
        ctx.kinds[path] = kind
    elif ctx.kinds and kind not in ctx.kinds[path.relative_to(root) if root else path]:
        raise ValueError("Path kind not as expected.")
    if root:
        (path.parent if file else path).mkdir(exist_ok=True, parents=True)
    return path


def resolve_path(value: Path | str, nxt: SerializerFunctionWrapHandler) -> str:
    """Resolve paths and serialize POSIX-style."""
    return nxt(Path(value).resolve().as_posix())


def ser_rooted_path(
    value: Path | str,
    nxt: SerializerFunctionWrapHandler,
    info: BoilercvPipelineSerializationInfo,
    key: Key,
) -> str:
    """Serialize paths POSIX-style, resolving if rooted."""
    ctx = info.context[BOILERCV_PIPELINE]
    return (
        resolve_path(value, nxt)
        if getattr(ctx.roots, key, None)
        else nxt(Path(value).as_posix())
    )


FilePathSerPosix: TypeAlias = Ann[FilePath, WrapSerializer(resolve_path)]
"""Directory path that serializes as POSIX."""
DirectoryPathSerPosix: TypeAlias = Ann[DirectoryPath, WrapSerializer(resolve_path)]
"""Directory path that serializes as POSIX."""
DataDir: TypeAlias = Ann[
    Path,
    ContextAfterValidator(partial(make_path, key="data", file=False)),
    ContextWrapSerializer(partial(ser_rooted_path, key="data")),
]
"""Data directory path made upon validation."""
DataFile: TypeAlias = Ann[
    Path,
    ContextAfterValidator(partial(make_path, key="data", file=True)),
    ContextWrapSerializer(partial(ser_rooted_path, key="data")),
]
"""Data file path made upon validation."""
DocsDir: TypeAlias = Ann[
    Path,
    ContextAfterValidator(partial(make_path, key="docs", file=False)),
    ContextWrapSerializer(partial(ser_rooted_path, key="docs")),
]
"""Docs directory path made upon validation."""
DocsFile: TypeAlias = Ann[
    Path,
    ContextAfterValidator(partial(make_path, key="docs", file=True)),
    ContextWrapSerializer(partial(ser_rooted_path, key="docs")),
]
"""Docs file path made upon validation."""


def get_path_time(time: str) -> str:
    """Get a path-friendly time string."""
    return time.replace(":", "-")
