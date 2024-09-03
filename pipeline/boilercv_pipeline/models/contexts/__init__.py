"""Contexts."""

from pathlib import Path

from pydantic import BaseModel, Field

from boilercv.contexts.types import Context
from boilercv_pipeline.config import const
from boilercv_pipeline.models.contexts.types import Kinds


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
    resolve_rooted: bool = True
    """Whether to resolve rooted paths when serializing."""


class BoilercvPipelineCtxDict(Context):
    """Boilercv pipeline context."""

    boilercv_pipeline: BoilercvPipelineCtx
