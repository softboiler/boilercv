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
    cines: DataDir = paths.cines


class Outs(StagePaths):
    large_sources: DataDir = paths.large_sources


@command(default_long=True, invoke="boilercv_pipeline.stages.convert.__main__.main")
class Convert(Params[Deps, Outs]):
    """Convert CINEs to NetCDF."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
