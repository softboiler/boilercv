from concurrent.futures import ProcessPoolExecutor
from functools import partial

from cappa.base import invoke

from boilercv_pipeline.stages.common import e230920
from boilercv_pipeline.stages.common.e230920 import get_times, submit_nb_process
from boilercv_pipeline.stages.common.e230920.types import DfNbOuts
from boilercv_pipeline.stages.e230920_find_contours import E230920FindContours


def main(params: E230920FindContours):
    save_df = partial(e230920.save_df, params=params)
    with ProcessPoolExecutor() as executor:
        for dt in get_times(params.deps.contours, params.pattern):
            params.time = dt
            submit_nb_process(executor, params=params, outs=DfNbOuts).add_done_callback(
                save_df
            )


if __name__ == "__main__":
    invoke(E230920FindContours)
