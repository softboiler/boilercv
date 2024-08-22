from pathlib import Path
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command, invoke
from pydantic import DirectoryPath, Field

from boilercv_pipeline.context import ContextModel
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.stages import StagePaths
from boilercv_pipeline.models.types.runtime import DataDir, DocsFile


class Deps(StagePaths):
    stage: DirectoryPath = Path(__file__).parent
    nb: DocsFile = paths.notebooks[stage.stem]
    e230920_objects: DataDir = paths.e230920_objects


class Outs(StagePaths):
    e230920_tracks: DataDir = paths.e230920_tracks


@command(
    invoke="boilercv_pipeline.stages.e230920_find_tracks.__main__.main",
    default_long=True,
)
class E230920FindTracks(ContextModel):
    """Export all tracks for this experiment."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)


if __name__ == "__main__":
    invoke(E230920FindTracks)
