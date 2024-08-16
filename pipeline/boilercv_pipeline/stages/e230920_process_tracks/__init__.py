from pathlib import Path
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command, invoke
from pydantic import DirectoryPath, Field

from boilercv_pipeline.context import ContextMergeModel
from boilercv_pipeline.models.paths import StagePaths, paths
from boilercv_pipeline.models.types.runtime import DataDir


class Deps(StagePaths):
    stage: DirectoryPath = Path(__file__).parent
    e230920_tracks: DataDir = paths.e230920_tracks


class Outs(StagePaths):
    e230920_processed_tracks: DataDir = paths.e230920_processed_tracks


@command(invoke="boilercv_pipeline.stages..__main__.main", default_long=True)
class E230920ProcessTracks(ContextMergeModel):
    """Process tracks."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)


if __name__ == "__main__":
    invoke(E230920ProcessTracks)
