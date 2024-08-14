"""Get mean absolute error of tracks."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Annotated

from boilercore.models import DefaultPathsModel
from cappa.arg import Arg
from cappa.base import command, invoke
from pydantic import BaseModel, Field

from boilercv_pipeline.models.notebooks import Notebooks
from boilercv_pipeline.models.paths import get_parser, paths
from boilercv_pipeline.stages.common.e230920 import get_e230920_times, submit_nb_process
from boilercv_pipeline.stages.common.e230920.types import Out


class Deps(DefaultPathsModel):
    root: Path = Field(default=paths.paths.root, exclude=True)
    stage: DirectoryPath = Path(__file__).parent
    e230920_processed_tracks: Path = paths.paths.e230920_processed_tracks


class Outs(DefaultPathsModel):
    root: Path = Field(default=paths.paths.root, exclude=True)
    e230920_mae: Path = paths.paths.e230920_mae


def main(args: E230920GetMae):
    with ProcessPoolExecutor() as executor:
        for dt in get_e230920_times(args.deps.e230920_processed_tracks):
            submit_nb_process(
                executor=executor,
                nb="e230920_get_mae",
                out=Out(key="mae", path=args.outs.e230920_mae, suffix=dt),
                params={"p": Notebooks(time=dt).model_dump()},
            )


@command(invoke=main, default_long=True)
class E230920GetMae(BaseModel):
    deps: Annotated[Deps, Arg(parse=get_parser(Deps), hidden=True)] = Deps()
    outs: Annotated[Outs, Arg(parse=get_parser(Deps), hidden=True)] = Outs()


if __name__ == "__main__":
    invoke(E230920GetMae)
