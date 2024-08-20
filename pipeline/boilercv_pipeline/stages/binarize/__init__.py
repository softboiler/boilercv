from pathlib import Path
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command
from pydantic import DirectoryPath, Field

from boilercv_pipeline.context import ContextMergeModel
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.stages import StagePaths
from boilercv_pipeline.models.types.runtime import DataDir


class Deps(StagePaths):
    stage: DirectoryPath = Path(__file__).parent
    large_sources: DataDir = paths.large_sources


class Outs(StagePaths):
    sources: DataDir = paths.sources
    rois: DataDir = paths.rois


@command(default_long=True, invoke="boilercv_pipeline.stages.binarize.__main__.main")
class Binarize(ContextMergeModel):
    """Binarize videos and export their ROIs."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
