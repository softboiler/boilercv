from pathlib import Path
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command, invoke
from pydantic import Field

from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.paths.types import StagePaths
from boilercv_pipeline.models.stages import Params
from boilercv_pipeline.models.types.runtime import (
    DataDir,
    DirectoryPathSerPosix,
    DocsFile,
)


class Deps(StagePaths):
    stage: DirectoryPathSerPosix = Path(__file__).parent
    nb: DocsFile = paths.notebooks[stage.stem]
    e230920_tracks: DataDir = paths.e230920_tracks


class Outs(StagePaths):
    e230920_processed_tracks: DataDir = paths.e230920_processed_tracks


@command(
    invoke="boilercv_pipeline.stages.e230920_process_tracks.__main__.main",
    default_long=True,
)
class E230920ProcessTracks(Params[Deps, Outs]):
    """Process tracks."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)


if __name__ == "__main__":
    invoke(E230920ProcessTracks)
