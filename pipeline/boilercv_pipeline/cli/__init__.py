"""Command-line interface."""

from collections.abc import Sized
from dataclasses import dataclass
from pathlib import Path
from types import NoneType
from typing import TypeAlias, get_args

from cappa.base import command
from cappa.subcommand import Subcommands
from more_itertools import one
from pydantic import BaseModel, Field, create_model
from yaml import safe_dump

from boilercv_pipeline.cli.types import Model_T
from boilercv_pipeline.models import dvc
from boilercv_pipeline.models.contexts import BOILERCV_PIPELINE, ROOTED
from boilercv_pipeline.models.dvc import OutFlags
from boilercv_pipeline.models.path import (
    BoilercvPipelineCtxModel,
    get_boilercv_pipeline_config,
)
from boilercv_pipeline.stages.binarize import Binarize
from boilercv_pipeline.stages.convert import Convert
from boilercv_pipeline.stages.fill import Fill
from boilercv_pipeline.stages.find_contours import FindContours
from boilercv_pipeline.stages.find_objects import FindObjects
from boilercv_pipeline.stages.find_tracks import FindTracks
from boilercv_pipeline.stages.get_mae import GetMae
from boilercv_pipeline.stages.get_thermal_data import GetThermalData
from boilercv_pipeline.stages.preview_binarized import PreviewBinarized
from boilercv_pipeline.stages.preview_filled import PreviewFilled
from boilercv_pipeline.stages.preview_gray import PreviewGray
from boilercv_pipeline.stages.skip_cloud import SkipCloud

Stages: TypeAlias = (
    SkipCloud
    | Convert
    | Binarize
    | PreviewGray
    | PreviewBinarized
    | FindContours
    | Fill
    | PreviewFilled
    | GetThermalData
    | FindObjects
    | FindTracks
    | GetMae
)


class Constants(BaseModel):
    """Constants."""

    dvc_out_config: OutFlags = OutFlags(persist=True)
    """Default `dvc.yaml` configuration for `outs`."""
    skip_cloud: list[str] = ["data/cines", "data/large_sources"]
    """These paths are too large and unwieldy to cache or push to cloud storage."""
    dvc_out_skip_cloud_config: OutFlags = OutFlags(
        cache=False, persist=True, push=False
    )
    """Default `dvc.yaml` configuration for `outs` that skip the cloud."""


const = Constants()


@dataclass
class Stage:
    """Stage."""

    commands: Subcommands[Stages]


@command(name="sync-dvc")
class SyncDVC:
    """Generate `dvc.yaml`."""

    def __call__(self):
        """Sync `dvc.yaml`."""
        BoilercvPipelineCtxModel.model_config = get_boilercv_pipeline_config(
            ROOTED, sync_dvc=True
        )
        ctx = create_model(  # pyright: ignore[reportCallIssue]
            "_Stages",
            __base__=BoilercvPipelineCtxModel,
            **{  # pyright: ignore[reportArgumentType]
                s.__module__.split(".")[-1]: (s, Field(default_factory=s))
                for s in get_args(Stages)
            },
        )().model_dump()["context"][BOILERCV_PIPELINE]
        (Path.cwd() / "params.yaml").write_text(
            encoding="utf-8",
            data=safe_dump(sort_keys=True, indent=2, data=ctx["dvc_params"]),
        )
        model = clear_defaults(dvc.DvcYamlModel.model_validate(ctx["dvc"]))
        for name, stage in model.stages.items():
            if isinstance(stage, dvc.Stage):
                stage = clear_defaults(stage)
                for i, out in enumerate(stage.outs):
                    if isinstance(out, dict):
                        stage.outs[i] = {
                            one(out.keys()): clear_defaults(one(out.values()))
                        }
                model.stages[name] = stage
        (Path.cwd() / "dvc.yaml").write_text(
            encoding="utf-8",
            data=safe_dump(
                sort_keys=False, indent=2, data=model.model_dump(exclude_none=True)
            ),
        )


def clear_defaults(model: Model_T) -> Model_T:
    """Clear default fields of a model."""
    model = model.model_copy(deep=True)
    for (field, value), info in zip(
        dict(model).items(), model.model_fields.values(), strict=True
    ):
        if (
            value is not None  # noqa: PLR0916
            and (ann := info.annotation)
            and (
                (isinstance(value, Sized) and not len(value))
                or (value == info.default and NoneType in get_args(ann))
            )
        ):
            setattr(model, field, None)
    return model


@dataclass
class BoilercvPipeline:
    """Pipeline."""

    commands: Subcommands[SyncDVC | Stage]
