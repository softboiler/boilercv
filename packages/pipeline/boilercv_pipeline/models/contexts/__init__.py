"""Contexts."""

from pathlib import Path

from context_models.types import Context
from pydantic import BaseModel, Field

from boilercv_pipeline.config import const
from boilercv_pipeline.models.contexts.types import Kinds

BOILERCV_PIPELINE = "boilercv_pipeline"
"""Context name for `boilercv_pipeline`."""


class Roots(BaseModel):
    """Root directories."""

    data: Path | None = None
    """Data."""
    docs: Path | None = None
    """Docs."""


ROOTED = Roots(data=const.root / const.data, docs=const.root / const.docs)
"""Paths rooted to their directories."""


class BoilercvPipelineContext(BaseModel):
    """Root directory context."""

    roots: Roots = Field(default_factory=Roots)
    """Root directories for different kinds of paths."""
    kinds: Kinds = Field(default_factory=dict)
    """Kind of each path."""
    track_kinds: bool = False
    """Whether to track kinds."""


class BoilercvPipelineContexts(Context):
    """Boilercv pipeline context."""

    boilercv_pipeline: BoilercvPipelineContext
