from concurrent.futures import ProcessPoolExecutor
from functools import partial

from cappa.base import invoke

from boilercv_pipeline.stages.common import e230920
from boilercv_pipeline.stages.common.e230920 import submit_nb_process
from boilercv_pipeline.stages.common.e230920.types import DfNbOuts
from boilercv_pipeline.stages.e230920_find_objects import E230920FindObjects


def main(params: E230920FindObjects):
    nb = params.deps.nb.read_text(encoding="utf-8")
    with ProcessPoolExecutor() as executor:
        for dep in params.deps.contours.paths:
            submit_nb_process(
                executor=executor, nb=nb, params=params, outs=DfNbOuts
            ).add_done_callback(
                partial(e230920.save_df, dfs=params.outs.dfs, dep=dep.path)
            )


if __name__ == "__main__":
    invoke(E230920FindObjects)
