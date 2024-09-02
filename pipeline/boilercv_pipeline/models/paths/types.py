"""Types."""

from typing import TypeVar

from boilercv_pipeline.models.path import (
    ROOTED,
    BoilercvPipelineCtxModel,
    get_boilercv_pipeline_config,
)
from boilercv_pipeline.models.paths import paths


class Stage(BoilercvPipelineCtxModel):
    """Base of stage models."""

    model_config = get_boilercv_pipeline_config(ROOTED, kinds_from=paths)


class StagePaths(Stage):
    """Paths for stage dependencies and outputs."""


Deps_T = TypeVar("Deps_T", bound=StagePaths, covariant=True)
"""Dependencies type."""
Outs_T = TypeVar("Outs_T", bound=StagePaths, covariant=True)
"""Outputs type."""
