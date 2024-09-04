"""Pipeline stage model and models at sub-pipeline stage granularity."""

from pydantic import BaseModel

from boilercv_pipeline.models.contexts import ROOTED
from boilercv_pipeline.models.path import (
    BoilercvPipelineCtxModel,
    get_boilercv_pipeline_config,
)
from boilercv_pipeline.models.paths import paths


class Stage(BoilercvPipelineCtxModel):
    """Base of pipeline stage models."""

    model_config = get_boilercv_pipeline_config(ROOTED, kinds_from=paths)


class StagePaths(Stage):
    """Paths for stage dependencies and outputs."""


class _DataStage(BaseModel):
    """Data stage in a pipeline stage."""

    src: str = "src"
    dst: str = "dst"


DataStage = _DataStage()
"""Data stage in a pipeline stage."""
