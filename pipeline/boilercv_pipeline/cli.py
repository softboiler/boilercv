"""Command-line interface."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from boilercore.models import apply_to_paths
from cappa.base import command
from cappa.subcommand import Subcommands
from pydantic import BaseModel, Field
from yaml import safe_dump

from boilercv_pipeline.context import ContextMergeModel
from boilercv_pipeline.stages.binarize import Binarize
from boilercv_pipeline.stages.convert import Convert
from boilercv_pipeline.stages.e230920_find_contours import E230920FindContours
from boilercv_pipeline.stages.e230920_find_objects import E230920FindObjects
from boilercv_pipeline.stages.e230920_find_tracks import E230920FindTracks
from boilercv_pipeline.stages.e230920_get_mae import E230920GetMae
from boilercv_pipeline.stages.e230920_get_thermal_data import E230920GetThermalData
from boilercv_pipeline.stages.e230920_merge_mae import E230920MergeMae
from boilercv_pipeline.stages.e230920_merge_tracks import E230920MergeTracks
from boilercv_pipeline.stages.e230920_plot_tracks import E230920PlotTracks
from boilercv_pipeline.stages.e230920_process_tracks import E230920ProcessTracks
from boilercv_pipeline.stages.fill import Fill
from boilercv_pipeline.stages.find_contours import FindContours
from boilercv_pipeline.stages.preview_binarized import PreviewBinarized
from boilercv_pipeline.stages.preview_filled import PreviewFilled
from boilercv_pipeline.stages.preview_gray import PreviewGray
from boilercv_pipeline.stages.skip_cloud import SkipCloud


class Constants(BaseModel):
    """Constants."""

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
        Binarize
        | SkipCloud
        | Convert
        | E230920FindContours
        | E230920FindObjects
        | E230920FindTracks
        | E230920GetMae
        | E230920MergeMae
        | E230920MergeTracks
        | E230920PlotTracks
        | E230920ProcessTracks
        | E230920GetThermalData
        | Fill
        | FindContours
        | PreviewBinarized
        | PreviewFilled
        | PreviewGray,
    ]


@command(name="sync-dvc")
class SyncDVC:
    """Generate `dvc.yaml`."""

    root: Path = Path.cwd()

    def __call__(self):
        """Sync `dvc.yaml`."""

        class Stages(ContextMergeModel):
            """Stages."""

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
            e230920_update_thermal_data: E230920GetThermalData = Field(
                default_factory=E230920GetThermalData
            )
            e230920_find_contours: E230920FindContours = Field(
                default_factory=E230920FindContours
            )
            e230920_find_objects: E230920FindObjects = Field(
                default_factory=E230920FindObjects
            )
            e230920_find_tracks: E230920FindTracks = Field(
                default_factory=E230920FindTracks
            )
            e230920_process_tracks: E230920ProcessTracks = Field(
                default_factory=E230920ProcessTracks
            )
            e230920_merge_tracks: E230920MergeTracks = Field(
                default_factory=E230920MergeTracks
            )
            e230920_plot_tracks: E230920PlotTracks = Field(
                default_factory=E230920PlotTracks
            )
            e230920_get_mae: E230920GetMae = Field(default_factory=E230920GetMae)
            e230920_merge_mae: E230920MergeMae = Field(default_factory=E230920MergeMae)

        stages: dict[str, Any] = {}
        for stage, stage_value in Stages().model_dump().items():
            for paths, paths_value in stage_value.items():
                stage_value[paths] = [
                    apply_to_paths(
                        path,
                        lambda path: (
                            path.relative_to(self.root) if path.is_absolute() else path
                        ).as_posix(),
                    )
                    for path in paths_value.values()
                ]
            stage_value["outs"] = [
                (
                    {out: const.dvc_out_skip_cloud_config}
                    if out in const.skip_cloud
                    else {out: const.dvc_out_config}
                )
                for out in stage_value["outs"]
            ]
            stages[stage] = {
                "cmd": f"boilercv-pipeline stage {stage.replace('_', '-')}",
                **stage_value,
            }
        dvc = self.root / "dvc.yaml"
        dvc.write_text(
            encoding="utf-8",
            data=safe_dump(sort_keys=False, indent=2, data={"stages": stages}),
        )


@dataclass
class BoilercvPipeline:
    """Pipeline."""

    commands: Subcommands[SyncDVC | Stage]
