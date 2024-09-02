from pathlib import Path
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command
from pydantic import Field

from boilercv_pipeline.models.path import DataDir, DirectoryPathSerPosix
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.paths.types import StagePaths
from boilercv_pipeline.models.stages import Params


class Deps(StagePaths):
    stage: DirectoryPathSerPosix = Path(__file__).parent
    sources: DataDir = paths.sources
    rois: DataDir = paths.rois


class Outs(StagePaths):
    contours: DataDir = paths.contours


@command(
    default_long=True, invoke="boilercv_pipeline.stages.find_contours.__main__.main"
)
class FindContours(Params[Deps, Outs]):
    """Get bubble contours."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
