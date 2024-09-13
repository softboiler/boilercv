"""Pipeline stage model and models at sub-pipeline stage granularity."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, field_validator

from boilercv.contexts import CONTEXT
from boilercv_pipeline.models import dvc
from boilercv_pipeline.models.contexts import BOILERCV_PIPELINE, ROOTED
from boilercv_pipeline.models.contexts.types import BoilercvPipelineValidationInfo
from boilercv_pipeline.models.path import (
    BoilercvPipelineCtxModel,
    DataDir,
    get_boilercv_pipeline_config,
)
from boilercv_pipeline.models.paths import paths


def get_dvc_stage(
    pipeline_type: type[BoilercvPipelineCtxModel], dvc_model: dvc.DvcYamlModel
) -> dvc.Stage:
    """Get DVC stage."""
    name = pipeline_type.__module__.split(".")[-1]
    if stage := dvc_model.stages.get(name):
        if not isinstance(stage, dvc.Stage):
            raise TypeError(f"Expected stage `{name}` to be a {dvc.Stage}.")
        return stage
    stage = dvc.Stage(cmd=f"boilercv-pipeline stage {name.replace('_', '-')}")
    dvc_model.stages[name] = stage
    return stage


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


class Stage(BoilercvPipelineCtxModel):
    """Base of pipeline stage models."""

    model_config = get_boilercv_pipeline_config(ROOTED, kinds_from=paths)


class StagePaths(BoilercvPipelineCtxModel):
    """Paths for stage dependencies and outputs."""

    model_config = get_boilercv_pipeline_config(ROOTED, kinds_from=paths)

    @field_validator("*", mode="after")
    @classmethod
    def dvc_validate_out(
        cls, value: Path, info: BoilercvPipelineValidationInfo
    ) -> Path:
        """Serialize path for `dvc.yaml`."""
        if (
            info.field_name != CONTEXT
            and (ctx := info.context[BOILERCV_PIPELINE]).sync_dvc
        ):
            stage = get_dvc_stage(cls, ctx.dvc)
            path = Path(value).resolve().relative_to(Path.cwd())
            if info.field_name == "plots":
                if plots := [p.as_posix() for p in path.iterdir()]:
                    stage.plots.extend(plots)
                return value
            path = path.as_posix()
            kind = "deps" if issubclass(cls, Deps) else "outs"
            getattr(stage, kind).append(
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
