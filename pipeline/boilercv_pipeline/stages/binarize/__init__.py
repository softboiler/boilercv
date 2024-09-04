from pathlib import Path
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command
from pydantic import Field

from boilercv_pipeline.models.params import Params
from boilercv_pipeline.models.path import DataDir, DirectoryPathSerPosix
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.stage import StagePaths


class Deps(StagePaths):
    stage: DirectoryPathSerPosix = Path(__file__).parent
    large_sources: DataDir = paths.large_sources


class Outs(StagePaths):
    sources: DataDir = paths.sources
    rois: DataDir = paths.rois


@command(default_long=True, invoke="boilercv_pipeline.stages.binarize.__main__.main")
class Binarize(Params[Deps, Outs]):
    """Binarize videos and export their ROIs."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
