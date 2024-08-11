"""Process tracks."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Annotated

from boilercore.models import DefaultPathsModel
from cappa.arg import Arg
from cappa.base import command, invoke
from pydantic import BaseModel, Field

from boilercv_pipeline.models import get_parser
from boilercv_pipeline.models.config import default
from boilercv_pipeline.models.notebooks import Notebooks
from boilercv_pipeline.stages.common.e230920 import get_e230920_times, submit_nb_process
from boilercv_pipeline.stages.common.e230920.types import Out


class Deps(DefaultPathsModel):
    root: Path = Field(default=default.paths.root, exclude=True)
    e230920_tracks: Path = default.paths.e230920_tracks


class Outs(DefaultPathsModel):
    root: Path = Field(default=default.paths.root, exclude=True)
    e230920_processed_tracks: Path = default.paths.e230920_processed_tracks


def main(args: E230920ProcessTracks):
    with ProcessPoolExecutor() as executor:
        for dt in get_e230920_times(args.deps.e230920_tracks):
            submit_nb_process(
                executor=executor,
                nb="e230920_process_tracks",
                out=Out(
                    key="processed_tracks",
                    path=args.outs.e230920_processed_tracks,
                    suffix=dt,
                ),
                params={"p": Notebooks(time=dt).model_dump()},
            )


@command(invoke=main, default_long=True)
class E230920ProcessTracks(BaseModel):
    deps: Annotated[Deps, Arg(parse=get_parser(Deps), hidden=True)] = Deps()
    outs: Annotated[Outs, Arg(parse=get_parser(Deps), hidden=True)] = Outs()


if __name__ == "__main__":
    invoke(E230920ProcessTracks)
