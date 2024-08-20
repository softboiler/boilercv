from pathlib import Path
from types import SimpleNamespace

from boilercore.notebooks.namespaces import get_nb_ns
from cappa.base import invoke

from boilercv_pipeline.stages.e230920_merge_mae import E230920MergeMae

PLOTS = Path("tests/plots/mae")
PLOTS.mkdir(parents=True, exist_ok=True)


def main(params: E230920MergeMae):
    plot_and_merge_mae(get_nb_ns(params.deps.nb.read_text(encoding="utf-8"), params))


def plot_and_merge_mae(ns: SimpleNamespace, params: E230920MergeMae):
    """Save mean absolute error plots."""
    ns.mae.to_hdf(
        params.outs.e230920_merged_mae,
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
