"""Get mean absolute error of tracks."""

from concurrent.futures import ProcessPoolExecutor

from cappa.base import invoke

from boilercv_pipeline.models.generated.stages.e230920_get_mae import E230920GetMae
from boilercv_pipeline.models.notebooks import Notebooks
from boilercv_pipeline.stages.common.e230920 import get_e230920_times, submit_nb_process
from boilercv_pipeline.stages.common.e230920.types import Out


def main(args: E230920GetMae):  # noqa: D103
    with ProcessPoolExecutor() as executor:
        for dt in get_e230920_times(args.deps.e230920_processed_tracks):
            submit_nb_process(
                executor=executor,
                nb="e230920_get_mae",
                out=Out(key="mae", path=args.outs.e230920_mae, suffix=dt),
                params={"p": Notebooks(time=dt).model_dump()},
            )


if __name__ == "__main__":
    invoke(E230920GetMae)
