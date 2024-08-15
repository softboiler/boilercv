"""Update thermal data for the experiment."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from boilercore.models import DefaultPathsModel
from boilercore.notebooks.namespaces import get_nb_ns
from cappa.arg import Arg
from cappa.base import command, invoke
from pydantic import BaseModel, DirectoryPath, Field

from boilercv_pipeline.models import get_parser
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.stages.common.e230920 import read_nb


class Deps(DefaultPathsModel):
    root: Path = Field(default=paths.paths.root, exclude=True)
    stage: DirectoryPath = Path(__file__).parent
    e230920_thermal_raw: Path = paths.paths.e230920_thermal_raw


class Outs(DefaultPathsModel):
    root: Path = Field(default=paths.paths.root, exclude=True)
    e230920_thermal: Path = paths.paths.e230920_thermal


def main(args: E230920UpdateThermalData):
    get_nb_ns(
        nb=read_nb("e230920_update_thermal_data"), attributes=["data"]
    ).data.to_hdf(args.outs.e230920_thermal, key="thermal", complib="zlib", complevel=9)


@command(invoke=main, default_long=True)
class E230920UpdateThermalData(BaseModel):
    deps: Annotated[Deps, Arg(parse=get_parser(Deps), hidden=True)] = Deps()
    outs: Annotated[Outs, Arg(parse=get_parser(Deps), hidden=True)] = Outs()


if __name__ == "__main__":
    invoke(E230920UpdateThermalData)
