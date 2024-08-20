from concurrent.futures import ProcessPoolExecutor

from cappa.base import invoke

from boilercv_pipeline.models.notebooks import Notebooks
from boilercv_pipeline.stages.common.e230920 import get_times, submit_nb_process
from boilercv_pipeline.stages.common.e230920.types import Out
from boilercv_pipeline.stages.e230920_get_mae import E230920GetMae


def main(params: E230920GetMae):
    with ProcessPoolExecutor() as executor:
        for dt in get_times(params.deps.e230920_processed_tracks, params.pattern):
            submit_nb_process(
                executor=executor,
                nb="e230920_get_mae",
                out=Out(key="mae", path=params.outs.e230920_mae, suffix=dt),
                params={"p": Notebooks(time=dt).model_dump()},
            )


if __name__ == "__main__":
    invoke(E230920GetMae)
