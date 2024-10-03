"""Pipeline stage model and models at sub-pipeline stage granularity."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Self

from context_models.validators import context_field_validator, context_model_validator
from pydantic import BaseModel
from pydantic.functional_validators import ModelWrapValidatorHandler

from boilercv_pipeline.models.contexts import ROOTED
from boilercv_pipeline.models.contexts.types import BoilercvPipelineValidationInfo
from boilercv_pipeline.models.path import (
    BoilercvPipelineContextStore,
    DataDir,
    get_boilercv_pipeline_config,
)
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.sync_dvc.validators import (
    dvc_add_param,
    dvc_prepare_stage,
    dvc_set_stage_path,
)


class Stage(BoilercvPipelineContextStore):
    """Base of pipeline stage models."""

    model_config = get_boilercv_pipeline_config(ROOTED, kinds_from=paths)

    @context_model_validator(mode="wrap")
    @classmethod
    def dvc_prepare_stage(
        cls,
        data: dict[str, Any],
        handler: ModelWrapValidatorHandler[Self],
        info: BoilercvPipelineValidationInfo,
    ) -> Self:
        """Prepare a pipeline stage for `dvc.yaml`."""
        return dvc_prepare_stage(data, handler, info, model=cls)

    @context_field_validator("*", mode="after")
    @classmethod
    def dvc_add_param(cls, value: Any, info: BoilercvPipelineValidationInfo) -> Any:
        """Add param to global parameters and stage command for `dvc.yaml`."""
        return dvc_add_param(value, info, fields=cls.model_fields)


class StagePaths(BoilercvPipelineContextStore):
    """Paths for stage dependencies and outputs."""

    model_config = get_boilercv_pipeline_config(ROOTED, kinds_from=paths)

    @context_field_validator("*", mode="after")
    @classmethod
    def dvc_set_stage_path(
        cls, path: Path, info: BoilercvPipelineValidationInfo
    ) -> Path:
        """Set stage path as a stage dep, plot, or out for `dvc.yaml`."""
        return dvc_set_stage_path(
            path, info, kind="deps" if issubclass(cls, Deps) else "outs"
        )


class Deps(StagePaths):
    """Stage dependency paths."""


class Outs(StagePaths):
    """Stage output paths."""


class DfsPlotsOuts(Outs):
    """Stage output paths including data frames and plots."""

    dfs: DataDir
    """Output data directory for this stage."""
    plots: DataDir
    """Output plots directory for this stage."""


class DataStage(BaseModel):
    """Data stage in a pipeline stage."""

    src: str = "src"
    """Source data for this stage."""
    dst: str = "dst"
    """Destination data for this stage."""
