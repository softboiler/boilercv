"""Plot mean absolute error of tracks."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from boilercore.notebooks.namespaces import get_nb_ns
from cappa.base import invoke

from boilercv_pipeline.stages.common.e230920 import read_nb
from boilercv_pipeline.stages.e230920_merge_mae import E230920MergeMae

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


if __name__ == "__main__":
    invoke(E230920MergeMae)
