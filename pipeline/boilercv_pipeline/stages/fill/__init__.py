from pathlib import Path
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command
from pydantic import DirectoryPath, Field

from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.paths.types import StagePaths
from boilercv_pipeline.models.stages import Params
from boilercv_pipeline.models.types.runtime import DataDir


class Deps(StagePaths):
    stage: DirectoryPath = Path(__file__).parent
    sources: DataDir = paths.sources
    rois: DataDir = paths.rois
    contours: DataDir = paths.contours


class Outs(StagePaths):
    filled: DataDir = paths.filled


@command(default_long=True, invoke="boilercv_pipeline.stages.fill.__main__.main")
class Fill(Params[Deps, Outs]):
    """Fill bubble contours."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
