from pathlib import Path
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command
from pydantic import Field

from boilercv_pipeline.models.params import Params
from boilercv_pipeline.models.path import DataDir, DataFile, DirectoryPathSerPosix
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.stage import StagePaths


class Deps(StagePaths):
    stage: DirectoryPathSerPosix = Path(__file__).parent
    filled: DataDir = paths.filled
    rois: DataDir = paths.rois


class Outs(StagePaths):
    filled_preview: DataFile = paths.filled_preview


@command(
    default_long=True, invoke="boilercv_pipeline.stages.preview_filled.__main__.main"
)
class PreviewFilled(Params[Deps, Outs]):
    """Update previews for the filled contours stage."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
