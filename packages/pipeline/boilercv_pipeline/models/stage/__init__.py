"""Pipeline stage model and models at sub-pipeline stage granularity."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from itertools import chain
from pathlib import Path
from typing import Any, Self

from cappa.arg import Arg
from context_models import CONTEXT
from context_models.validators import context_field_validator, context_model_validator
from more_itertools import first
from pydantic import BaseModel
from pydantic.functional_validators import ModelWrapValidatorHandler

import boilercv_pipeline
from boilercv_pipeline.models import dvc
from boilercv_pipeline.models import dvc as _dvc
from boilercv_pipeline.models.contexts import DVC, ROOTED
from boilercv_pipeline.models.contexts.types import BoilercvPipelineValidationInfo
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

    @context_model_validator(mode="wrap")
    @classmethod
    def dvc_prepare_stage(
        cls,
        data: dict[str, Any],
        handler: ModelWrapValidatorHandler[Self],
        info: BoilercvPipelineValidationInfo,
    ) -> Self:
        """Validate param for `dvc.yaml`."""
        if not (dvc := info.context.get(DVC)):
            return handler(data)
        name = cls.__module__.split(".")[-1]
        if dvc.model.stages.get(name):
            return handler(data)
        dvc.stage = _dvc.Stage(cmd="")
        dvc.model.stages[name] = dvc.stage
        sep = " "
        dvc.stage.cmd = sep.join([
            f"./Invoke-Uv.ps1 {boilercv_pipeline.__name__.replace('_', '-')}",
            f"stage {name.replace('_', '-')}",
        ])
        self = handler(data)
        dvc.stage.cmd = f'pwsh -Command "{dvc.stage.cmd}"'
        return self

    @context_field_validator("*", mode="after")
    @classmethod
    def dvc_add_param(cls, value: Any, info: BoilercvPipelineValidationInfo) -> Any:
        # sourcery skip: low-code-quality
        """Add param to `dvc.yaml`."""
        if (
            (dvc := info.context.get(DVC))
            and not first(
                (
                    m
                    for m in cls.model_fields[info.field_name].metadata
                    if isinstance(m, Arg)
                ),
                default=Arg,
            ).hidden
            and (info.field_name not in dvc.stage.params)
        ) and isinstance(value, Sequence | bool | int | float | complex | datetime):
            sep = " "
            name = info.field_name
            arg = name.replace("_", "-")
            if not dvc.params.get(name):
                if isinstance(value, bool):
                    dvc.params[name] = f"--{arg}" if value else f"--no-{arg}"
                elif not isinstance(value, str) and isinstance(value, Sequence):
                    values = []
                    for v in value:
                        if isinstance(v, Path):
                            v = v.as_posix()
                        elif not isinstance(v, bool | int | float | complex | datetime):
                            return value
                        values.append(v)
                    dvc.params[name] = sep.join(
                        chain.from_iterable((arg, v) for v in values)
                    )
                else:
                    dvc.params[name] = value
            if isinstance(value, bool) or (
                not isinstance(value, str) and isinstance(value, Sequence)
            ):
                args = [f"${{{name}}}"]
            else:
                args = [f"--{arg}", f"${{{name}}}"]
            dvc.stage.cmd = sep.join([
                *(
                    dvc.stage.cmd
                    if isinstance(dvc.stage.cmd, list)
                    else dvc.stage.cmd.split(sep)
                ),
                *args,
            ])
            dvc.stage.params.append(name)
        return value


class StagePaths(BoilercvPipelineContextStore):
    """Paths for stage dependencies and outputs."""

    model_config = get_boilercv_pipeline_config(ROOTED, kinds_from=paths)

    @context_field_validator("*", mode="after")
    @classmethod
    def dvc_validate_out(
        cls, value: Path, info: BoilercvPipelineValidationInfo
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
    """Output data directory for this stage."""
    plots: DataDir
    """Output plots directory for this stage."""


class DataStage(BaseModel):
    """Data stage in a pipeline stage."""

    src: str = "src"
    """Source data for this stage."""
    dst: str = "dst"
    """Destination data for this stage."""
