"""Types used at runtime."""

from __future__ import annotations

from functools import cached_property, partial
from pathlib import Path
from typing import Annotated, ClassVar, TypeAlias

from cappa.arg import Arg
from pydantic import (
    AfterValidator,
    BaseModel,
    Field,
    SerializerFunctionWrapHandler,
    WrapSerializer,
    computed_field,
)

from boilercv_pipeline.config import const
from boilercv_pipeline.context import ContextModel
from boilercv_pipeline.context.types import (
    Context,
    ContextPluginSettings,
    PluginConfigDict,
    SerializationInfo,
    ValidationInfo,
)
from boilercv_pipeline.models.types import Key, Kind, Kinds


class Roots(BaseModel):
    """Root directories."""

    data: Path | None = None
    """Data."""
    docs: Path | None = None
    """Docs."""


ROOTED = Roots(data=const.data, docs=const.docs)
"""Paths rooted to their directories."""


class BoilercvPipelineCtx(BaseModel):
    """Root directory context."""

    roots: Roots = Field(default_factory=Roots)
    """Root directories for different kinds of paths."""
    kinds: Kinds = Field(default_factory=dict)
    """Kind of each path."""
    track_kinds: bool = False
    """Whether to track kinds."""

    @computed_field
    @cached_property
    def check_kinds(self) -> bool:
        """Whether kinds were pre-populated and should be checked against."""
        return bool(self.kinds)


class BoilercvPipelineCtxDict(Context):
    """Boilercv pipeline context."""

    boilercv_pipeline: BoilercvPipelineCtx


BoilercvPipelineConfigDict: TypeAlias = PluginConfigDict[
    ContextPluginSettings[BoilercvPipelineCtxDict]
]
BoilercvPipelineValidationInfo: TypeAlias = ValidationInfo[BoilercvPipelineCtxDict]
BoilercvPipelineSerializationInfo: TypeAlias = SerializationInfo[
    BoilercvPipelineCtxDict
]


def get_boilercv_pipeline_context(
    roots: Roots | None = None,
    kinds_from: BoilercvPipelineCtxModel | None = None,
    track_kinds: bool = False,
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
        )
    )


def get_boilercv_pipeline_config(
    roots: Roots | None = None,
    kinds_from: BoilercvPipelineCtxModel | None = None,
    track_kinds: bool = False,
) -> BoilercvPipelineConfigDict:
    """Model config for {mod}`~boilercv_pipeline`."""
    return PluginConfigDict(
        plugin_settings=ContextPluginSettings(
            context=get_boilercv_pipeline_context(
                roots=roots, kinds_from=kinds_from, track_kinds=track_kinds
            )
        )
    )


class BoilercvPipelineCtxModel(ContextModel):
    """Context model for {mod}`~boilercv_pipeline`."""

    model_config: ClassVar[BoilercvPipelineConfigDict] = (  # pyright: ignore[reportIncompatibleVariableOverride]
        get_boilercv_pipeline_config()
    )
    context: Annotated[Context, Arg(hidden=True)] = Context()
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
        (path.parent if file else path).mkdir(exist_ok=True, parents=True)
    if (
        ctx.check_kinds
        and kind not in ctx.kinds[path.relative_to(root) if root else path]
    ):
        raise ValueError("Path kind not as expected.")
    if ctx.track_kinds:
        ctx.kinds[path] = kind
    return path


def ser_path(value: Path | str, nxt: SerializerFunctionWrapHandler) -> str:
    """Resolve paths and serialize POSIX-style."""
    return nxt(value.as_posix() if isinstance(value, Path) else value)


DataDir = Annotated[
    Path,
    AfterValidator(partial(make_path, key="data", file=False)),
    WrapSerializer(ser_path),
]
"""Data directory path made upon validation."""
DataFile = Annotated[
    Path,
    AfterValidator(partial(make_path, key="data", file=True)),
    WrapSerializer(ser_path),
]
"""Data file path made upon validation."""
DocsDir = Annotated[
    Path,
    AfterValidator(partial(make_path, key="docs", file=False)),
    WrapSerializer(ser_path),
]
"""Docs directory path made upon validation."""
DocsFile = Annotated[
    Path,
    AfterValidator(partial(make_path, key="docs", file=True)),
    WrapSerializer(ser_path),
]
"""Docs file path made upon validation."""
