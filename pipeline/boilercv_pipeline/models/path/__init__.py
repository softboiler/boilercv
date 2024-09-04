"""Path models."""

from __future__ import annotations

from functools import partial
from pathlib import Path
from re import search
from typing import Annotated, ClassVar, TypeAlias

from boilercore.paths import ISOLIKE, dt_fromisolike
from cappa.arg import Arg
from pydantic import (
    AfterValidator,
    DirectoryPath,
    FilePath,
    SerializerFunctionWrapHandler,
    WrapSerializer,
)

from boilercv.contexts import ContextModel
from boilercv.contexts.types import Context, ContextPluginSettings, PluginConfigDict
from boilercv_pipeline.models.contexts import (
    BoilercvPipelineCtx,
    BoilercvPipelineCtxDict,
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
    kinds_from: BoilercvPipelineCtxModel | None = None,
    track_kinds: bool = False,
    resolve_rooted: bool = True,
) -> BoilercvPipelineCtxDict:
    """Context for {mod}`~boilercv_pipeline`."""
    ctx_from: BoilercvPipelineCtxDict = getattr(
        kinds_from,
        "context",
        BoilercvPipelineCtxDict(boilercv_pipeline=BoilercvPipelineCtx()),
    )
    return BoilercvPipelineCtxDict(
        boilercv_pipeline=BoilercvPipelineCtx(
            roots=roots or Roots(),
            kinds=ctx_from["boilercv_pipeline"].kinds,
            track_kinds=track_kinds,
            resolve_rooted=resolve_rooted,
        )
    )


def get_boilercv_pipeline_config(
    roots: Roots | None = None,
    kinds_from: BoilercvPipelineCtxModel | None = None,
    track_kinds: bool = False,
    resolve_rooted: bool = True,
) -> BoilercvPipelineConfigDict:
    """Model config for {mod}`~boilercv_pipeline`."""
    return PluginConfigDict(
        plugin_settings=ContextPluginSettings(
            context=get_boilercv_pipeline_context(
                roots=roots,
                kinds_from=kinds_from,
                track_kinds=track_kinds,
                resolve_rooted=resolve_rooted,
            )
        )
    )


HiddenContext: TypeAlias = Annotated[Context, Arg(hidden=True)]


class BoilercvPipelineCtxModel(ContextModel):
    """Context model for {mod}`~boilercv_pipeline`."""

    model_config: ClassVar[BoilercvPipelineConfigDict] = (  # pyright: ignore[reportIncompatibleVariableOverride]
        get_boilercv_pipeline_config()
    )
    context: HiddenContext = Context()
    _context_handlers: ClassVar = {"boilercv_pipeline": BoilercvPipelineCtx}


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
    ctx = info.context["boilercv_pipeline"]
    root = getattr(ctx.roots, key, None)
    kind = make_path_args[(key, file)]
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
    ctx = info.context["boilercv_pipeline"]
    return (
        resolve_path(value, nxt)
        if ctx.resolve_rooted and getattr(ctx.roots, key, None)
        else nxt(Path(value).as_posix())
    )


FilePathSerPosix: TypeAlias = Annotated[FilePath, WrapSerializer(resolve_path)]
"""Directory path that serializes as POSIX."""
DirectoryPathSerPosix: TypeAlias = Annotated[
    DirectoryPath, WrapSerializer(resolve_path)
]
"""Directory path that serializes as POSIX."""
DataDir: TypeAlias = Annotated[
    Path,
    AfterValidator(partial(make_path, key="data", file=False)),
    WrapSerializer(partial(ser_rooted_path, key="data")),
]
"""Data directory path made upon validation."""
DataFile: TypeAlias = Annotated[
    Path,
    AfterValidator(partial(make_path, key="data", file=True)),
    WrapSerializer(partial(ser_rooted_path, key="data")),
]
"""Data file path made upon validation."""
DocsDir: TypeAlias = Annotated[
    Path,
    AfterValidator(partial(make_path, key="docs", file=False)),
    WrapSerializer(partial(ser_rooted_path, key="docs")),
]
"""Docs directory path made upon validation."""
DocsFile: TypeAlias = Annotated[
    Path,
    AfterValidator(partial(make_path, key="docs", file=True)),
    WrapSerializer(partial(ser_rooted_path, key="docs")),
]
"""Docs file path made upon validation."""


def get_path_time(time: str) -> str:
    """Get a path-friendly time string."""
    return time.replace(":", "-")
