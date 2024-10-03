"""Command-line interface."""

from __future__ import annotations

from dataclasses import dataclass

from cappa.subcommand import Subcommands

from boilercv_pipeline.cli.experiments import Trackpy
from boilercv_pipeline.stages.binarize import Binarize
from boilercv_pipeline.stages.convert import Convert
from boilercv_pipeline.stages.fill import Fill
from boilercv_pipeline.stages.find_contours import FindContours
from boilercv_pipeline.stages.find_objects import FindObjects
from boilercv_pipeline.stages.find_tracks import FindTracks
from boilercv_pipeline.stages.get_thermal_data import GetThermalData
from boilercv_pipeline.stages.preview_binarized import PreviewBinarized
from boilercv_pipeline.stages.preview_filled import PreviewFilled
from boilercv_pipeline.stages.preview_gray import PreviewGray
from boilercv_pipeline.stages.skip_cloud import SkipCloud
from boilercv_pipeline.sync_dvc import SyncDvc


@dataclass
class Stage:
    """Run a pipeline stage."""

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
    ]


@dataclass
class Exp:
    """Run a pipeline experiment."""

    commands: Subcommands[Trackpy]


@dataclass
class BoilercvPipeline:
    """Run the research data pipeline."""

    commands: Subcommands[SyncDvc | Stage | Exp]
