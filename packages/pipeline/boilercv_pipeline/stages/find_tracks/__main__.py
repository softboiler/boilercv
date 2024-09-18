from concurrent.futures import ProcessPoolExecutor
from functools import partial

from cappa.base import invoke
from more_itertools import one

from boilercv_pipeline.dfs import save_df
from boilercv_pipeline.models.path import get_time
from boilercv_pipeline.nbs import callbacks, submit_nb_process
from boilercv_pipeline.plotting import save_plots
from boilercv_pipeline.stages.find_tracks import FindTracks as Params


def main(params: Params):
    nb = params.deps.nb.read_text(encoding="utf-8")
    dfs = params.outs.dfs
    with ProcessPoolExecutor() as executor:
        for filled, filled_slicers in zip(
            params.filled, params.filled_slicers, strict=True
        ):
            for field, value in {
                "filled": filled,
                "filled_slicers": filled_slicers,
                "dfs": dfs / f"{dfs.name}_{get_time(filled)}.h5",
            }.items():
                setattr(params, field, [value])
            submit_nb_process(
                executor=executor, nb=nb, params=params
            ).add_done_callback(
                partial(
                    callbacks,
                    callbacks=[
                        lambda f: save_df(df=f.result().dfs.dst, path=one(params.dfs)),
                        lambda f: save_plots(
                            plots=f.result().plots, path=params.outs.plots
                        ),
                    ],
                )
            )


if __name__ == "__main__":
    invoke(Params)
