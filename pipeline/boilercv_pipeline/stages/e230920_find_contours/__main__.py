"""Export all contours for this experiment."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor

from cappa.base import invoke

from boilercv_pipeline.stages.common.e230920 import get_e230920_times, submit_nb_process
from boilercv_pipeline.stages.common.e230920.types import Out
from boilercv_pipeline.stages.e230920_find_contours import E230920FindContours


def main(args: E230920FindContours):
    with ProcessPoolExecutor() as executor:
        for dt in get_e230920_times(args.deps.contours):
            submit_nb_process(
                executor=executor,
                nb="e230920_find_contours",
                out=Out(key="contours", path=args.outs.e230920_contours, suffix=dt),
                params={"FRAMES": None, "COMPARE_WITH_TRACKPY": False, "TIME": dt},
            )


if __name__ == "__main__":
    invoke(E230920FindContours)
