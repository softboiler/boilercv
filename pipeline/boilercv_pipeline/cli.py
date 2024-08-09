"""Command-line interface."""

from dataclasses import dataclass

from cappa.base import command
from cappa.subcommand import Subcommands

from boilercv_pipeline.models.generated.stages.binarize import Binarize
from boilercv_pipeline.models.generated.stages.convert import Convert
from boilercv_pipeline.models.generated.stages.fill import Fill
from boilercv_pipeline.models.generated.stages.find_contours import FindContours
from boilercv_pipeline.models.generated.stages.flatten_data_dir import FlattenDataDir
from boilercv_pipeline.models.generated.stages.preview_binarized import PreviewBinarized
from boilercv_pipeline.models.generated.stages.preview_filled import PreviewFilled
from boilercv_pipeline.models.generated.stages.preview_gray import PreviewGray


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
