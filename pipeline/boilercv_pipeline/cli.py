"""Command-line interface."""

from dataclasses import dataclass

from cappa.base import command
from cappa.subcommand import Subcommands

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
class Stages:
    """Stages."""

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


@dataclass
class BoilercvPipeline:
    """Pipeline."""

    commands: Subcommands[SyncParams | SyncStagesLiterals | Stages]
