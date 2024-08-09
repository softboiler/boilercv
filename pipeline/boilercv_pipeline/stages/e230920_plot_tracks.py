"""Export correlation plots for tracks."""

from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from types import SimpleNamespace

from boilercv_pipeline.stages.common.e230920 import (
    EXP_TIMES,
    get_path_time,
    submit_nb_process,
)

PLOTS = Path("tests/plots/tracks")
PLOTS.mkdir(exist_ok=True)


def main():  # noqa: D103
    with ProcessPoolExecutor() as executor:
        for dt in EXP_TIMES:
            submit_nb_process(
                executor=executor,
                nb="plot_tracks",
                name="tracks",
                params={"TIME": dt.isoformat()},
                process=export_track_plot,
            )


def export_track_plot(_path: Path, ns: SimpleNamespace):
    """Export object centers and sizes."""
    ns.figure.savefig(PLOTS / f"{get_path_time(ns.TIME)}.png")


if __name__ == "__main__":
    main()
