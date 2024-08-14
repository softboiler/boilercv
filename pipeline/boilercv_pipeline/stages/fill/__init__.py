from pathlib import Path
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command
from pydantic import DirectoryPath, Field

from boilercv_pipeline.contexts import ContextsMergeModel
from boilercv_pipeline.models.paths import DataDir, MatchedPaths, paths


class Deps(MatchedPaths):
    stage: DirectoryPath = Path(__file__).parent
    sources: DataDir = paths.sources
    contours: DataDir = paths.contours


class Outs(MatchedPaths):
    filled: DataDir = paths.filled


@command(default_long=True, invoke="boilercv_pipeline.stages.fill.__main__.main")
class Fill(ContextsMergeModel):
    """Fill bubble contours."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
