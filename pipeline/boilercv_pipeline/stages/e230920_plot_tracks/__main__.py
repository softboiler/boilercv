from pathlib import Path
from types import SimpleNamespace

from cappa.base import invoke

from boilercv_pipeline.stages.common.e230920 import get_path_time
from boilercv_pipeline.stages.e230920_plot_tracks import E230920PlotTracks


def main(_params: E230920PlotTracks):
    pass


def export_track_plot(ns: SimpleNamespace):
    """Export object centers and sizes."""
    plots = Path("tests/plots/tracks")
    plots.mkdir(parents=True, exist_ok=True)
    ns.figure.savefig(plots / f"{get_path_time(ns.TIME)}.png")


if __name__ == "__main__":
    invoke(E230920PlotTracks)
