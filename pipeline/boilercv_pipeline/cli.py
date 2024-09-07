"""Command-line interface."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cappa.base import command
from cappa.subcommand import Subcommands
from pydantic import BaseModel, Field
from yaml import safe_dump

from boilercv.mappings import apply
from boilercv_pipeline.models.contexts import ROOTED
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

    dvc_keys: list[str] = ["deps", "outs"]
    """Keys expected in a DVC stage."""
    dvc_out_config: dict[str, bool] = {"persist": True}
    """Default `dvc.yaml` configuration for `outs`."""
    skip_cloud: list[str] = ["data/cines", "data/large_sources"]
    """These paths are too large and unwieldy to cache or push to cloud storage."""
    dvc_out_skip_cloud_config: dict[str, bool] = {
        "persist": True,
        "cache": False,
        "push": False,
    }
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

        def process_path(path: Path) -> str:
            path = Path(path)
            return (
                path.relative_to(self.root) if path.is_absolute() else path
            ).as_posix()

        stages: dict[str, Any] = {}
        raw_stages = Stages().model_dump()
        del raw_stages["context"]
        for stage_name, stage in raw_stages.items():
            for k in const.dvc_keys:
                del stage[k]["context"]
            for k in [k for k in stage if k not in const.dvc_keys]:
                del stage[k]
            stage["deps"] = [process_path(v) for v in stage["deps"].values()]
            if (plots := stage["outs"].pop("plots", None)) and (
                plots := [p.as_posix() for p in Path(plots).iterdir()]
            ):
                stage["plots"] = plots
            stage["outs"] = [
                (
                    {out: const.dvc_out_skip_cloud_config}
                    if out in const.skip_cloud
                    else {out: const.dvc_out_config}
                )
                for out in stage["outs"].values()
            ]
            stages[stage_name] = {
                "cmd": f"boilercv-pipeline stage {stage_name.replace('_', '-')}",
                **stage,
            }
        dvc = self.root / "dvc.yaml"

        def drop_context(n):
            n.pop("context", None)
            return n

        dvc.write_text(
            encoding="utf-8",
            data=safe_dump(
                sort_keys=False,
                indent=2,
                data={
                    "stages": apply(
                        stages,
                        node_fun=drop_context,
                        leaf_fun=(
                            lambda leaf: process_path(leaf)
                            if isinstance(leaf, Path)
                            else leaf
                        ),
                    )
                },
            ),
        )


@dataclass
class BoilercvPipeline:
    """Pipeline."""

    commands: Subcommands[SyncDVC | Stage]
