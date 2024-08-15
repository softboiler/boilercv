"""Export all contours for this experiment."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Annotated

from boilercore.models import DefaultPathsModel
from cappa.arg import Arg
from cappa.base import command, invoke
from pydantic import BaseModel, DirectoryPath, Field

from boilercv_pipeline.models import get_parser
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.stages.common.e230920 import get_e230920_times, submit_nb_process
from boilercv_pipeline.stages.common.e230920.types import Out


class Deps(DefaultPathsModel):
    root: Path = Field(default=paths.paths.root, exclude=True)
    stage: DirectoryPath = Path(__file__).parent
    contours: Path = paths.paths.contours


class Outs(DefaultPathsModel):
    root: Path = Field(default=paths.paths.root, exclude=True)
    e230920_contours: Path = paths.paths.e230920_contours


def main(args: E230920FindContours):
    with ProcessPoolExecutor() as executor:
        for dt in get_e230920_times(args.deps.contours):
            submit_nb_process(
                executor=executor,
                nb="e230920_find_contours",
                out=Out(key="contours", path=args.outs.e230920_contours, suffix=dt),
                params={"FRAMES": None, "COMPARE_WITH_TRACKPY": False, "TIME": dt},
            )


@command(invoke=main, default_long=True)
class E230920FindContours(BaseModel):
    deps: Annotated[Deps, Arg(parse=get_parser(Deps), hidden=True)] = Deps()
    outs: Annotated[Outs, Arg(parse=get_parser(Deps), hidden=True)] = Outs()


if __name__ == "__main__":
    invoke(E230920FindContours)
