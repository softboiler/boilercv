"""Command-line interface."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from boilercore.models import apply_to_paths
from cappa.base import command
from cappa.subcommand import Subcommands
from pydantic import BaseModel
from yaml import safe_dump

from boilercv_pipeline.stages.binarize import Binarize
from boilercv_pipeline.stages.convert import Convert
from boilercv_pipeline.stages.e230920_find_contours import E230920FindContours
from boilercv_pipeline.stages.e230920_find_objects import E230920FindObjects
from boilercv_pipeline.stages.e230920_find_tracks import E230920FindTracks
from boilercv_pipeline.stages.e230920_get_mae import E230920GetMae
from boilercv_pipeline.stages.e230920_merge_mae import E230920MergeMae
from boilercv_pipeline.stages.e230920_merge_tracks import E230920MergeTracks
from boilercv_pipeline.stages.e230920_plot_tracks import E230920PlotTracks
from boilercv_pipeline.stages.e230920_process_tracks import E230920ProcessTracks
from boilercv_pipeline.stages.e230920_update_thermal_data import (
    E230920UpdateThermalData,
)
from boilercv_pipeline.stages.fill import Fill
from boilercv_pipeline.stages.find_contours import FindContours
from boilercv_pipeline.stages.flatten_data_dir import FlattenDataDir
from boilercv_pipeline.stages.preview_binarized import PreviewBinarized
from boilercv_pipeline.stages.preview_filled import PreviewFilled
from boilercv_pipeline.stages.preview_gray import PreviewGray


@command(invoke="boilercv_pipeline.models.Params")
class SyncParams:
    """Synchronize parameters."""


@command(invoke="boilercv_pipeline.models.types.generated.sync_stages")
class SyncStagesLiterals:
    """Sync stages literals."""


@dataclass
class Stage:
    """Stage."""

    commands: Subcommands[
        Binarize
        | Convert
        | E230920FindContours
        | E230920FindObjects
        | E230920FindTracks
        | E230920GetMae
        | E230920MergeMae
        | E230920MergeTracks
        | E230920PlotTracks
        | E230920ProcessTracks
        | E230920UpdateThermalData
        | Fill
        | FindContours
        | FlattenDataDir
        | PreviewBinarized
        | PreviewFilled
        | PreviewGray,
    ]


def generate_dvc_yaml(root: Path | None = None):
    """Generate `dvc.yaml`."""
    root = root or Path.cwd()

    class Stages(BaseModel):
        """Stages."""

        binarize: Binarize = Binarize()
        convert: Convert = Convert()
        flatten_data_dir: FlattenDataDir = FlattenDataDir()
        preview_gray: PreviewGray = PreviewGray()
        preview_binarized: PreviewBinarized = PreviewBinarized()
        find_contours: FindContours = FindContours()
        fill: Fill = Fill()
        preview_filled: PreviewFilled = PreviewFilled()
        e230920_update_thermal_data: E230920UpdateThermalData = (
            E230920UpdateThermalData()
        )
        e230920_find_contours: E230920FindContours = E230920FindContours()
        e230920_find_objects: E230920FindObjects = E230920FindObjects()
        e230920_find_tracks: E230920FindTracks = E230920FindTracks()
        e230920_process_tracks: E230920ProcessTracks = E230920ProcessTracks()
        e230920_merge_tracks: E230920MergeTracks = E230920MergeTracks()
        e230920_plot_tracks: E230920PlotTracks = E230920PlotTracks()
        e230920_get_mae: E230920GetMae = E230920GetMae()
        e230920_merge_mae: E230920MergeMae = E230920MergeMae()

    stages: dict[str, Any] = {}
    for stage, stage_value in Stages().model_dump().items():
        for paths, paths_value in stage_value.items():
            stage_value[paths] = [
                apply_to_paths(path, lambda path: path.relative_to(root).as_posix())
                for path in paths_value.values()
            ]
        stage_value["outs"] = [{out: {"persist": True}} for out in stage_value["outs"]]
        stages[stage] = {
            "cmd": f"boilercv_pipeline stage {stage.replace('_', '-')}",
            **stage_value,
        }
    (root / "dvc.yaml").write_text(
        encoding="utf-8",
        data=safe_dump(sort_keys=False, indent=2, data={"stages": stages}),
    )


@dataclass
class BoilercvPipeline:
    """Pipeline."""

    commands: Subcommands[SyncParams | SyncStagesLiterals | Stage]
