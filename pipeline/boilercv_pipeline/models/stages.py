"""Stage models."""

from pathlib import Path
from typing import Generic, TypeAlias, TypeVar

from pydantic import BaseModel, Field

from boilercv_pipeline.context import ContextMergeModel
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.types.runtime import (
    BoilercvPipelineCtxModel,
    Roots,
    get_boilercv_pipeline_config,
)

ROOTED = Roots(data=Path("data"), docs=Path("docs"))
"""Paths rooted to their directories."""


class Stage(BoilercvPipelineCtxModel):
    """Base of stage models."""

    model_config = get_boilercv_pipeline_config(
        ROOTED, kinds_from=paths, track_kinds=True
    )


class StagePaths(Stage):
    """Paths for stage dependencies and outputs."""


Deps_T = TypeVar("Deps_T", bound=StagePaths, covariant=True)
"""Dependencies type."""
Outs_T = TypeVar("Outs_T", bound=StagePaths, covariant=True)
"""Outputs type."""


class Plotting(BaseModel):
    """Plotting parameters."""

    scale: float = 1.6
    """Plot scale."""
    marker_scale: float = 20
    """Marker scale."""

    @property
    def size(self) -> float:
        """Marker size."""
        return self.scale * self.marker_scale

    @property
    def font_scale(self) -> float:
        """Font scale."""
        return self.scale


class Params(ContextMergeModel, Generic[Deps_T, Outs_T]):
    """Stage parameters."""

    deps: Deps_T
    """Stage dependencies."""
    outs: Outs_T
    """Stage outputs."""
    plotting: Plotting = Field(default_factory=Plotting)
    """Plotting parameters."""


AnyParams: TypeAlias = Params[StagePaths, StagePaths]
