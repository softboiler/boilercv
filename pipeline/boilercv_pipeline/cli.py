"""Command-line interface."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cappa.base import command
from cappa.subcommand import Subcommands
from pydantic import BaseModel, Field
from yaml import safe_dump

from boilercv_pipeline.models import dvc
from boilercv_pipeline.models.contexts import ROOTED
from boilercv_pipeline.models.dvc import DvcYamlModel, OutFlags
from boilercv_pipeline.models.params.types import AnyParams
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

    commands: Subcommands[
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
    ]


@command(name="sync-dvc")
class SyncDVC:
    """Generate `dvc.yaml`."""

    root: Path = Path.cwd()

    def __call__(self):
        """Sync `dvc.yaml`."""

        class Stages(BoilercvPipelineCtxModel):
            """Stages."""

            model_config = get_boilercv_pipeline_config(ROOTED, resolve_rooted=False)

            skip_cloud: SkipCloud = Field(default_factory=SkipCloud)
            convert: Convert = Field(default_factory=Convert)
            binarize: Binarize = Field(default_factory=Binarize)
            preview_gray: PreviewGray = Field(default_factory=PreviewGray)
            preview_binarized: PreviewBinarized = Field(
                default_factory=PreviewBinarized
            )
            find_contours: FindContours = Field(default_factory=FindContours)
            fill: Fill = Field(default_factory=Fill)
            preview_filled: PreviewFilled = Field(default_factory=PreviewFilled)
            get_thermal_data: GetThermalData = Field(default_factory=GetThermalData)
            find_objects: FindObjects = Field(default_factory=FindObjects)
            find_tracks: FindTracks = Field(default_factory=FindTracks)
            get_mae: GetMae = Field(default_factory=GetMae)

        def process_path(path: Path | str) -> str:
            path = Path(path)
            return (
                path.relative_to(self.root) if path.is_absolute() else path
            ).as_posix()

        stages: dict[str, dvc.Stage] = {}
        all_params: dict[str, AnyParams] = dict(Stages())
        del all_params["context"]
        for name, params in all_params.items():
            outs: dict[str, str | dict[str, Any]] = params.outs.model_dump()
            plots: str | None = outs.pop("plots", None)  # pyright: ignore[reportAssignmentType]
            stages[name] = dvc.Stage(
                cmd=f"boilercv-pipeline stage {name.replace('_', '-')}",
                deps=(
                    [
                        process_path(d)
                        for k, d in params.deps.model_dump().items()
                        if k != "context"
                    ]
                    or None
                ),
                outs=(
                    [
                        (
                            {out: const.dvc_out_skip_cloud_config}
                            if out in const.skip_cloud
                            else {out: const.dvc_out_config}
                        )
                        for out in outs.values()
                        if isinstance(out, str | Path)
                    ]
                    or None
                ),
                plots=(
                    ([p.as_posix() for p in Path(plots).iterdir()] if plots else None)
                    or None
                ),
            )
        (self.root / "dvc.yaml").write_text(
            encoding="utf-8",
            data=safe_dump(
                sort_keys=False,
                indent=2,
                data=DvcYamlModel(stages=stages).model_dump(exclude_none=True),
            ),
        )


@dataclass
class BoilercvPipeline:
    """Pipeline."""

    commands: Subcommands[SyncDVC | Stage]
