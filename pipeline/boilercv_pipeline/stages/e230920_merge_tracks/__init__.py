from pathlib import Path
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command, invoke
from pydantic import Field

from boilercv_pipeline.models.params import Params
from boilercv_pipeline.models.path import DataDir, DataFile, DirectoryPathSerPosix
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.stage import StagePaths


class Deps(StagePaths):
    stage: DirectoryPathSerPosix = Path(__file__).parent
    e230920_processed_tracks: DataDir = paths.e230920_processed_tracks


class Outs(StagePaths):
    e230920_merged_tracks: DataFile = paths.e230920_merged_tracks


@command(
    invoke="boilercv_pipeline.stages.e230920_merge_tracks.__main__.main",
    default_long=True,
)
class E230920MergeTracks(Params[Deps, Outs]):
    """Merge tracks."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)


if __name__ == "__main__":
    invoke(E230920MergeTracks)
