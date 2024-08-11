"""Plot mean absolute error of tracks."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Annotated

from boilercore.models import DefaultPathsModel
from boilercore.notebooks.namespaces import get_nb_ns
from cappa.arg import Arg
from cappa.base import command, invoke
from pydantic import BaseModel, Field

from boilercv_pipeline.models import get_parser
from boilercv_pipeline.models.config import default
from boilercv_pipeline.stages.common.e230920 import read_nb


class Deps(DefaultPathsModel):
    root: Path = Field(default=default.paths.root, exclude=True)
    stage: Path = Path(__file__)
    e230920_mae: Path = default.paths.e230920_mae


class Outs(DefaultPathsModel):
    root: Path = Field(default=default.paths.root, exclude=True)
    e230920_merged_mae: Path = default.paths.e230920_merged_mae


PLOTS = Path("tests/plots/mae")
PLOTS.mkdir(exist_ok=True)


def main(args: E230920MergeMae):
    plot_and_merge_mae(get_nb_ns(nb=read_nb("e230920_merge_mae")), args)


def plot_and_merge_mae(ns: SimpleNamespace, args: E230920MergeMae):
    """Save mean absolute error plots."""
    ns.mae.to_hdf(
        args.outs.e230920_merged_mae,
        format="table",
        key="mae",
        complib="zlib",
        complevel=9,
    )
    path = PLOTS / "mae.png"
    for i, fig in enumerate(ns.FIGURES):
        fig.savefig(path.with_stem(f"{path.stem}_{i}"))


@command(invoke=main, default_long=True)
class E230920MergeMae(BaseModel):
    deps: Annotated[Deps, Arg(parse=get_parser(Deps), hidden=True)] = Deps()
    outs: Annotated[Outs, Arg(parse=get_parser(Deps), hidden=True)] = Outs()


if __name__ == "__main__":
    invoke(E230920MergeMae)
