from concurrent.futures import ProcessPoolExecutor

from cappa.base import invoke

from boilercv_pipeline.models.notebooks import Notebooks
from boilercv_pipeline.stages.common.e230920 import get_times, submit_nb_process
from boilercv_pipeline.stages.common.e230920.types import Out
from boilercv_pipeline.stages.e230920_process_tracks import E230920ProcessTracks


def main(params: E230920ProcessTracks):
    with ProcessPoolExecutor() as executor:
        for dt in get_times(params.deps.e230920_tracks, params.pattern):
            submit_nb_process(
                executor=executor,
                nb="e230920_process_tracks",
                out=Out(
                    key="processed_tracks",
                    path=params.outs.e230920_processed_tracks,
                    suffix=dt,
                ),
                params={"p": Notebooks(time=dt).model_dump()},
            )


if __name__ == "__main__":
    invoke(E230920ProcessTracks)
