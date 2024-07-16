"""Plot mean absolute error of tracks."""

from pathlib import Path
from types import SimpleNamespace

from boilercore.notebooks.namespaces import get_nb_ns

from boilercv_pipeline.experiments.e230920_subcool import MERGED_MAE, read_nb

PLOTS = Path("tests/plots/mae")
PLOTS.mkdir(exist_ok=True)


def main():  # noqa: D103
    plot_and_merge_mae(get_nb_ns(nb=read_nb("merge_mae")))


def plot_and_merge_mae(ns: SimpleNamespace):
    """Save mean absolute error plots."""
    ns.mae.to_hdf(MERGED_MAE, format="table", key="mae", complib="zlib", complevel=9)
    path = PLOTS / "mae.png"
    for i, fig in enumerate(ns.FIGURES):
        fig.savefig(path.with_stem(f"{path.stem}_{i}"))


if __name__ == "__main__":
    main()
