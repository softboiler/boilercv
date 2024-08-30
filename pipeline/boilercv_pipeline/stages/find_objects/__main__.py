from concurrent.futures import ProcessPoolExecutor
from functools import partial

from cappa.base import invoke

from boilercv_pipeline.models.deps import DirSlicer
from boilercv_pipeline.stages.common.e230920 import (
    callbacks,
    const,
    save_df,
    save_future_plots,
    submit_nb_process,
)
from boilercv_pipeline.stages.find_objects import FindObjects, Nb


def main(params: FindObjects):
    nb = params.deps.nb.read_text(encoding="utf-8")
    all_contours = DirSlicer(
        path=params.deps.contours, include_patterns=const.single_sample_include_pattern
    )
    all_filled = DirSlicer(
        path=params.deps.filled,
        include_patterns=const.single_sample_include_pattern,
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
                executor=executor, nb=nb, params=params
            ).add_done_callback(
                partial(
                    callbacks,
                    callbacks=[
                        partial(save_df, dfs=params.outs.dfs, dep=contours),
                        partial(
                            save_future_plots, plots=params.outs.plots, dep=contours
                        ),
                    ],
                )
            )


if __name__ == "__main__":
    invoke(FindObjects)
