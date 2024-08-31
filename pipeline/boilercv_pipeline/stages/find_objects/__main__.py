from concurrent.futures import ProcessPoolExecutor
from functools import partial

from cappa.base import invoke
from more_itertools import one

from boilercv_pipeline.stages.common.e230920 import (
    callbacks,
    get_time,
    save_df,
    save_plots,
    submit_nb_process,
)
from boilercv_pipeline.stages.find_objects import FindObjects as Params


def main(params: Params):
    nb = params.deps.nb.read_text(encoding="utf-8")
    dfs = params.outs.dfs
    with ProcessPoolExecutor() as executor:
        for contours, filled, filled_slicers in zip(
            params.contours, params.filled, params.filled_slicers, strict=True
        ):
            for field, value in {
                "contours": contours,
                "filled": filled,
                "filled_slicers": filled_slicers,
                "dfs": (dfs / f"{dfs.name}_{get_time(contours)}.h5"),
            }.items():
                setattr(params, field, value)
            submit_nb_process(
                executor=executor, nb=nb, params=params
            ).add_done_callback(
                partial(
                    callbacks,
                    callbacks=[
                        lambda f: save_df(df=f.result().df, path=one(params.dfs)),
                        lambda f: save_plots(
                            figs=f.result().plots, plots=params.outs.plots
                        ),
                    ],
                )
            )


if __name__ == "__main__":
    invoke(Params)
