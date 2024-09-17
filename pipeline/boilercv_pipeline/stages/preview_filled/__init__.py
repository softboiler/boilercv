from pathlib import Path
from typing import Annotated as Ann

from cappa.arg import Arg
from cappa.base import command
from pydantic import Field

from boilercv_pipeline.models import stage
from boilercv_pipeline.models.params import Params
from boilercv_pipeline.models.path import DataDir, DataFile, DirectoryPathSerPosix
from boilercv_pipeline.models.paths import paths


class Deps(stage.Deps):
    stage: DirectoryPathSerPosix = Path(__file__).parent
    filled: DataDir = paths.filled
    rois: DataDir = paths.rois


class Outs(stage.Outs):
    filled_preview: DataFile = paths.filled_preview


@command(
    default_long=True, invoke="boilercv_pipeline.stages.preview_filled.__main__.main"
)
class PreviewFilled(Params[Deps, Outs]):
    """Update previews for the filled contours stage."""

    deps: Ann[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Ann[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
