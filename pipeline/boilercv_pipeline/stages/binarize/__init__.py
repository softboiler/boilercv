from pathlib import Path
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command
from pydantic import DirectoryPath, Field

from boilercv_pipeline.contexts import ContextsMergeModel
from boilercv_pipeline.models.paths import DataDir, MatchedPaths, paths


class Deps(MatchedPaths):
    stage: DirectoryPath = Path(__file__).parent
    large_sources: DataDir = paths.large_sources


class Outs(MatchedPaths):
    sources: DataDir = paths.sources
    rois: DataDir = paths.rois


@command(default_long=True, invoke="boilercv_pipeline.stages.binarize.__main__.main")
class Binarize(ContextsMergeModel):
    """Binarize videos and export their ROIs."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
