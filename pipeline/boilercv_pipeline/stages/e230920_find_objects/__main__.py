from concurrent.futures import ProcessPoolExecutor

from cappa.base import invoke

from boilercv_pipeline.models.notebooks import Notebooks
from boilercv_pipeline.stages.common.e230920 import get_e230920_times, submit_nb_process
from boilercv_pipeline.stages.common.e230920.types import Out
from boilercv_pipeline.stages.e230920_find_objects import E230920FindObjects


def main(args: E230920FindObjects):
    with ProcessPoolExecutor() as executor:
        for dt in get_e230920_times(args.deps.e230920_contours):
            submit_nb_process(
                executor=executor,
                nb="e230920_find_objects",
                out=Out(key="objects", path=args.outs.e230920_objects, suffix=dt),
                params={"p": Notebooks(time=dt).model_dump()},
            )


if __name__ == "__main__":
    invoke(E230920FindObjects)
