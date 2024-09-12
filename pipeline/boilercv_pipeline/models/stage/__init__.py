"""Pipeline stage model and models at sub-pipeline stage granularity."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, SerializerFunctionWrapHandler, field_serializer

from boilercv_pipeline.models import dvc
from boilercv_pipeline.models.contexts import BOILERCV_PIPELINE, ROOTED
from boilercv_pipeline.models.contexts.types import (
    BoilercvPipelineFieldSerializationInfo,
    BoilercvPipelineSerializationInfo,
)
from boilercv_pipeline.models.path import (
    BoilercvPipelineCtxModel,
    DataDir,
    get_boilercv_pipeline_config,
)
from boilercv_pipeline.models.paths import paths


class Stage(BoilercvPipelineCtxModel):
    """Base of pipeline stage models."""

    model_config = get_boilercv_pipeline_config(ROOTED, kinds_from=paths)


class StagePaths(BoilercvPipelineCtxModel):
    """Paths for stage dependencies and outputs."""

    model_config = get_boilercv_pipeline_config(ROOTED, kinds_from=paths)


class Deps(StagePaths):
    """Stage dependency paths."""

    @field_serializer("*", mode="wrap")
    def dvc_serialize_dep(
        self,
        value: dict[str, Any] | Path,
        nxt: SerializerFunctionWrapHandler,
        info: BoilercvPipelineFieldSerializationInfo,
    ) -> Any:
        """Serialize dep for `dvc.yaml`."""
        return dvc_serialize_path(self, value, nxt, info, "deps")


class Outs(StagePaths):
    """Stage output paths."""

    @field_serializer("*", mode="wrap")
    def dvc_serialize_out(
        self,
        value: dict[str, Any] | Path,
        nxt: SerializerFunctionWrapHandler,
        info: BoilercvPipelineFieldSerializationInfo,
    ) -> Any:
        """Serialize out for `dvc.yaml`."""
        return dvc_serialize_path(self, value, nxt, info, "outs")


class DfsPlotsOuts(Outs):
    """Stage output paths including data frames and plots."""

    dfs: DataDir
    plots: DataDir


class DataStage(BaseModel):
    """Data stage in a pipeline stage."""

    src: str = "src"
    dst: str = "dst"


def dvc_serialize_path(
    model: BaseModel,
    value: dict[str, Any] | Path,
    nxt: SerializerFunctionWrapHandler,
    info: BoilercvPipelineFieldSerializationInfo,
    kind: str,
) -> Any:
    """Serialize dep for `dvc.yaml`."""
    ser: dict[str, Any] | str = nxt(value)
    if isinstance(ser, str) and (stage := get_dvc_stage(model, info)):
        getattr(stage, kind).append(Path(ser).relative_to(Path.cwd()).as_posix())
    return ser


def get_dvc_stage(
    model: BaseModel,
    info: BoilercvPipelineSerializationInfo | BoilercvPipelineFieldSerializationInfo,
) -> dvc.Stage | None:
    """Get DVC stage."""
    return (
        stage
        if (
            (ctx := info.context[BOILERCV_PIPELINE]).sync_dvc
            and (stage := ctx.dvc.stages.get(model.__module__.split(".")[-1]))
            and isinstance(stage, dvc.Stage)
        )
        else None
    )
