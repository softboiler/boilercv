"""Export all tracks for this experiment."""

from concurrent.futures import ProcessPoolExecutor

from boilercv_pipeline.models.notebooks import Notebooks
from boilercv_pipeline.stages.common.e230920 import EXP_TIMES, submit_nb_process


def main():  # noqa: D103
    with ProcessPoolExecutor() as executor:
        for dt in EXP_TIMES:
            submit_nb_process(
                executor=executor,
                nb="find_tracks",
                name="tracks",
                params={"p": Notebooks(time=dt.isoformat()).model_dump()},
            )


if __name__ == "__main__":
    main()
