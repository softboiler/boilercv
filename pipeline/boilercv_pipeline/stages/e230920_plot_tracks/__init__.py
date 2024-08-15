from pathlib import Path
from types import SimpleNamespace
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command, invoke
from pydantic import BaseModel, DirectoryPath, Field

from boilercv_pipeline.models.paths import StagePaths, paths
from boilercv_pipeline.stages.common.e230920 import get_path_time
from boilercv_pipeline.stages.common.e230920.types import Out


class Deps(StagePaths):
    stage: DirectoryPath = Path(__file__).parent
    e230920_merged_tracks: Path = paths.e230920_merged_tracks


class Outs(StagePaths): ...


PLOTS = Path("tests/plots/tracks")
PLOTS.mkdir(exist_ok=True)


def export_track_plot(ns: SimpleNamespace, _out: Out):
    """Export object centers and sizes."""
    ns.figure.savefig(PLOTS / f"{get_path_time(ns.TIME)}.png")


@command(invoke="boilercv_pipeline.stages..__main__.main", default_long=True)
class E230920PlotTracks(BaseModel):
    """Export correlation plots for tracks."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)


if __name__ == "__main__":
    invoke(E230920PlotTracks)
