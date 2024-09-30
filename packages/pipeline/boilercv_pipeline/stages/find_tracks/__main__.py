from concurrent.futures import ProcessPoolExecutor
from functools import partial

from more_itertools import one

from boilercv_pipeline.dfs import save_dfs
from boilercv_pipeline.models.path import get_time
from boilercv_pipeline.nbs import callbacks, submit_nb_process
from boilercv_pipeline.parser import invoke
from boilercv_pipeline.plotting import save_plots
from boilercv_pipeline.stages.find_tracks import FindTracks as Params


def main(params: Params):
    nb = params.deps.nb.read_text(encoding="utf-8")
    with ProcessPoolExecutor() as executor:
        for filled, filled_slicers, objects, dfs in zip(
            params.filled,
            params.filled_slicers,
            params.objects,
            params.dfs,
            strict=True,
        ):
            _params = params.model_copy(deep=True)
            time = get_time(filled)
            for field, value in {
                "filled": filled,
                "filled_slicers": filled_slicers,
                "objects": objects,
                "dfs": dfs,
            }.items():
                setattr(_params, field, [value])
            submit_nb_process(
                executor=executor, nb=nb, params=_params
            ).add_done_callback(
                partial(
                    callbacks,
                    callbacks=[
                        partial(
                            lambda f, p: save_dfs(
                                dfs=f.result().dfs.model_dump(), path=p
                            ),
                            p=one(_params.dfs),
                        ),
                        partial(
                            lambda f, p, s: save_plots(
                                plots=f.result().plots, path=p, suffix=s
                            ),
                            p=_params.outs.plots,
                            s=time,
                        ),
                    ],
                )
            )


if __name__ == "__main__":
    invoke(Params)
