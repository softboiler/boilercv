"""Types used at runtime."""

from __future__ import annotations

from functools import cached_property, partial
from pathlib import Path
from typing import Annotated, ClassVar, TypeAlias

from pydantic import AfterValidator, BaseModel, Field, computed_field

from boilercv_pipeline.context import ContextMergeModel
from boilercv_pipeline.context.types import (
    Context,
    ContextPluginSettings,
    PluginConfigDict,
    ValidationInfo,
)
from boilercv_pipeline.models.types import Kind, Kinds


class Roots(BaseModel):
    """Root directories."""

    data: Path | None = None
    """Data."""
    docs: Path | None = None
    """Docs."""


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


def get_boilercv_pipeline_context(
    roots: Roots | None = None,
    kinds_from: BoilercvPipelineCtxModel | None = None,
    track_kinds: bool = False,
) -> BoilercvPipelineCtxDict:
    """Context for {mod}`~boilercv_pipeline`."""
    ctx_from: BoilercvPipelineCtxDict = getattr(
        kinds_from,
        "_context",
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


class BoilercvPipelineCtxModel(ContextMergeModel):
    """Context model for {mod}`~boilercv_pipeline`."""

    model_config: ClassVar[BoilercvPipelineConfigDict] = (  # pyright: ignore[reportIncompatibleVariableOverride]
        get_boilercv_pipeline_config()
    )


kinds: dict[Kind, tuple[str, bool]] = {
    "DataDir": ("data", False),
    "DataFile": ("data", True),
    "DocsDir": ("docs", False),
    "DocsFile": ("docs", True),
}
"""Kinds and their {func}`~boilercv_pipeline.models.paths.make_path` args."""
make_path_args: dict[tuple[str, bool], Kind] = {v: k for k, v in kinds.items()}
"""{func}`~boilercv_pipeline.models.paths.make_path` args and their kinds."""


def make_path(
    key: str, file: bool, path: Path, info: BoilercvPipelineValidationInfo
) -> Path:
    """Check path kind and make a directory and its parents or a file's parents."""
    ctx = info.context["boilercv_pipeline"]
    if ctx.check_kinds and make_path_args[(key, file)] not in ctx.kinds[path]:
        raise ValueError("Path kind not as expected.")
    if ctx.track_kinds:
        ctx.kinds[path] = make_path_args[(key, file)]
    if (root := getattr(ctx.roots, key, None)) and not path.is_absolute():
        path = root / path
        (path.parent if file else path).mkdir(exist_ok=True, parents=True)
    return path


DataDir = Annotated[Path, AfterValidator(partial(make_path, *kinds["DataDir"]))]
"""Data directory path made upon validation."""
DataFile = Annotated[Path, AfterValidator(partial(make_path, *kinds["DataFile"]))]
"""Data file path made upon validation."""
DocsDir = Annotated[Path, AfterValidator(partial(make_path, *kinds["DocsDir"]))]
"""Docs directory path made upon validation."""
DocsFile = Annotated[Path, AfterValidator(partial(make_path, *kinds["DocsFile"]))]
"""Docs file path made upon validation."""
