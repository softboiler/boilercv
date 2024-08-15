from pathlib import Path
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command, invoke
from pydantic import BaseModel, DirectoryPath, Field

from boilercv_pipeline.models.paths import StagePaths, paths


class Deps(StagePaths):
    stage: DirectoryPath = Path(__file__).parent
    e230920_mae: Path = paths.e230920_mae


class Outs(StagePaths):
    e230920_merged_mae: Path = paths.e230920_merged_mae


PLOTS = Path("tests/plots/mae")
PLOTS.mkdir(exist_ok=True)


@command(invoke="boilercv_pipeline.stages..__main__.main", default_long=True)
class E230920MergeMae(BaseModel):
    """Plot mean absolute error of tracks."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)


if __name__ == "__main__":
    invoke(E230920MergeMae)
