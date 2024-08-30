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
    DataFile,
    DirectoryPathSerPosix,
    DocsFile,
)


class Deps(StagePaths):
    stage: DirectoryPathSerPosix = Path(__file__).parent
    nb: DocsFile = paths.notebooks[stage.stem]
    e230920_mae: DataDir = paths.e230920_mae


class Outs(StagePaths):
    e230920_merged_mae: DataFile = paths.e230920_merged_mae


@command(
    invoke="boilercv_pipeline.stages.e230920_merge_mae.__main__.main", default_long=True
)
class E230920MergeMae(Params[Deps, Outs]):
    """Plot mean absolute error of tracks."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)


if __name__ == "__main__":
    invoke(E230920MergeMae)
