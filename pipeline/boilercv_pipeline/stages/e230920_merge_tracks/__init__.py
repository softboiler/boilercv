from pathlib import Path
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command, invoke
from pydantic import DirectoryPath, Field

from boilercv_pipeline.context import ContextModel
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.stages import StagePaths
from boilercv_pipeline.models.types.runtime import DataDir, DataFile


class Deps(StagePaths):
    stage: DirectoryPath = Path(__file__).parent
    e230920_processed_tracks: DataDir = paths.e230920_processed_tracks


class Outs(StagePaths):
    e230920_merged_tracks: DataFile = paths.e230920_merged_tracks


@command(
    invoke="boilercv_pipeline.stages.e230920_merge_tracks.__main__.main",
    default_long=True,
)
class E230920MergeTracks(ContextModel):
    """Merge tracks."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)


if __name__ == "__main__":
    invoke(E230920MergeTracks)
