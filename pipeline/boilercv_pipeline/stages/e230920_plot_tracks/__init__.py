from pathlib import Path
from types import SimpleNamespace
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command, invoke
from pydantic import DirectoryPath, Field

from boilercv_pipeline.context import ContextModel
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.paths.types import StagePaths
from boilercv_pipeline.models.types.runtime import DataFile, DocsFile
from boilercv_pipeline.stages.common.e230920 import get_path_time


class Deps(StagePaths):
    stage: DirectoryPath = Path(__file__).parent
    nb: DocsFile = paths.notebooks[stage.stem]
    e230920_merged_tracks: DataFile = paths.e230920_merged_tracks


class Outs(StagePaths): ...


PLOTS = Path("tests/plots/tracks")
PLOTS.mkdir(exist_ok=True)


def export_track_plot(ns: SimpleNamespace):
    """Export object centers and sizes."""
    ns.figure.savefig(PLOTS / f"{get_path_time(ns.TIME)}.png")


@command(
    invoke="boilercv_pipeline.stages.e230920_plot_tracks.__main__.main",
    default_long=True,
)
class E230920PlotTracks(ContextModel):
    """Export correlation plots for tracks."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)


if __name__ == "__main__":
    invoke(E230920PlotTracks)