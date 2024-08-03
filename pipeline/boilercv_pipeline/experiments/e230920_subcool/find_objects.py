"""Export all centers for this experiment."""

from concurrent.futures import ProcessPoolExecutor

from boilercv_pipeline.experiments.e230920_subcool import EXP_TIMES, submit_nb_process
from boilercv_pipeline.models.notebooks import Notebooks


def main():  # noqa: D103
    with ProcessPoolExecutor() as executor:
        for dt in EXP_TIMES:
            submit_nb_process(
                executor=executor,
                nb="find_objects",
                name="objects",
                params={"p": Notebooks(time=dt.isoformat()).model_dump()},
            )


if __name__ == "__main__":
    main()
