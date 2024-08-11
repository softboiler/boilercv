"""Export correlation plots for tracks."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from typing import Annotated

from boilercore.models import DefaultPathsModel
from cappa.arg import Arg
from cappa.base import command, invoke
from pydantic import BaseModel, Field

from boilercv_pipeline.models import get_parser
from boilercv_pipeline.models.config import default
from boilercv_pipeline.models.notebooks import Notebooks
from boilercv_pipeline.stages.common.e230920 import (
    get_e230920_times,
    get_path_time,
    submit_nb_process,
)
from boilercv_pipeline.stages.common.e230920.types import Out


class Deps(DefaultPathsModel):
    root: Path = Field(default=default.paths.root, exclude=True)
    e230920_merged_tracks: Path = default.paths.e230920_merged_tracks


class Outs(DefaultPathsModel):
    root: Path = Field(default=default.paths.root, exclude=True)


PLOTS = Path("tests/plots/tracks")
PLOTS.mkdir(exist_ok=True)


def main(args: E230920PlotTracks):
    with ProcessPoolExecutor() as executor:
        for dt in get_e230920_times(args.deps.e230920_merged_tracks):
            submit_nb_process(
                executor=executor,
                nb="e230920_get_mae",
                out=Out(key="mae", suffix=dt),
                params={"p": Notebooks(time=dt).model_dump()},
                process=export_track_plot,
            )


def export_track_plot(ns: SimpleNamespace, _out: Out):
    """Export object centers and sizes."""
    ns.figure.savefig(PLOTS / f"{get_path_time(ns.TIME)}.png")


@command(invoke=main, default_long=True)
class E230920PlotTracks(BaseModel):
    deps: Annotated[Deps, Arg(parse=get_parser(Deps), hidden=True)] = Deps()
    outs: Annotated[Outs, Arg(parse=get_parser(Deps), hidden=True)] = Outs()


if __name__ == "__main__":
    invoke(E230920PlotTracks)
