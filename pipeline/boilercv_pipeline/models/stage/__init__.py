"""Pipeline stage model and models at sub-pipeline stage granularity."""

from __future__ import annotations

from pathlib import Path

from context_models import CONTEXT
from context_models.validators import context_field_validator
from context_models.validators.types import ContextValidationInfo
from pydantic import BaseModel

from boilercv_pipeline.models import dvc
from boilercv_pipeline.models.contexts import DVC, ROOTED, BoilercvPipelineContexts
from boilercv_pipeline.models.path import (
    BoilercvPipelineContextStore,
    DataDir,
    get_boilercv_pipeline_config,
)
from boilercv_pipeline.models.paths import paths


class Constants(BaseModel):
    """Constants."""

    dvc_out_config: dvc.OutFlags = dvc.OutFlags(persist=True)
    """Default `dvc.yaml` configuration for `outs`."""
    skip_cloud: list[str] = ["data/cines", "data/large_sources"]
    """These paths are too large and unwieldy to cache or push to cloud storage."""
    dvc_out_skip_cloud_config: dvc.OutFlags = dvc.OutFlags(
        cache=False, persist=True, push=False
    )
    """Default `dvc.yaml` configuration for `outs` that skip the cloud."""


const = Constants()


class Stage(BoilercvPipelineContextStore):
    """Base of pipeline stage models."""

    model_config = get_boilercv_pipeline_config(ROOTED, kinds_from=paths)


class StagePaths(BoilercvPipelineContextStore):
    """Paths for stage dependencies and outputs."""

    model_config = get_boilercv_pipeline_config(ROOTED, kinds_from=paths)

    @context_field_validator("*", mode="after")
    @classmethod
    def dvc_validate_out(
        cls, value: Path, info: ContextValidationInfo[BoilercvPipelineContexts]
    ) -> Path:
        """Serialize path for `dvc.yaml`."""
        if info.field_name != CONTEXT and (dvc := info.context.get(DVC)):
            path = Path(value).resolve().relative_to(Path.cwd())
            if info.field_name == "plots":
                if plots := [p.as_posix() for p in path.iterdir()]:
                    dvc.stage.plots.extend(plots)
                return value
            path = path.as_posix()
            kind = "deps" if issubclass(cls, Deps) else "outs"
            getattr(dvc.stage, kind).append(
                path
                if kind == "deps"
                else (
                    {path: const.dvc_out_skip_cloud_config}
                    if path in const.skip_cloud
                    else {path: const.dvc_out_config}
                )
            )
        return value


class Deps(StagePaths):
    """Stage dependency paths."""


class Outs(StagePaths):
    """Stage output paths."""


class DfsPlotsOuts(Outs):
    """Stage output paths including data frames and plots."""

    dfs: DataDir
    plots: DataDir


class DataStage(BaseModel):
    """Data stage in a pipeline stage."""

    src: str = "src"
    dst: str = "dst"
