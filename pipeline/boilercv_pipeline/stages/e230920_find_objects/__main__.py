from concurrent.futures import ProcessPoolExecutor
from functools import partial

from cappa.base import invoke

from boilercv_pipeline.models.deps import DirSlicer
from boilercv_pipeline.stages.common import e230920
from boilercv_pipeline.stages.common.e230920 import submit_nb_process
from boilercv_pipeline.stages.common.e230920.types import DfNbOuts
from boilercv_pipeline.stages.e230920_find_objects import E230920FindObjects, Nb


def main(params: E230920FindObjects):
    nb = params.deps.nb.read_text(encoding="utf-8")
    all_contours = DirSlicer(
        path=params.deps.contours, include_patterns=params.include_patterns
    )
    all_filled = DirSlicer(
        path=params.deps.filled,
        include_patterns=params.include_patterns,
        slicer_patterns=params.slicer_patterns,
    )
    with ProcessPoolExecutor() as executor:
        for contours, filled in zip(all_contours.paths, all_filled.paths, strict=True):
            params.nb = Nb(
                contours=contours,
                filled=filled,
                filled_slicers=all_filled.path_slicers[filled],
            )
            submit_nb_process(
                executor=executor, nb=nb, params=params, outs=DfNbOuts
            ).add_done_callback(
                partial(e230920.save_df, dfs=params.outs.dfs, dep=contours)
            )


if __name__ == "__main__":
    invoke(E230920FindObjects)
