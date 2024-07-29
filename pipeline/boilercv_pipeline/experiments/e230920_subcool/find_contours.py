"""Export all contours for this experiment."""

from concurrent.futures import ProcessPoolExecutor

from boilercv_pipeline.experiments.e230920_subcool import (
    DAY,
    get_times,
    submit_nb_process,
)
from boilercv_pipeline.models.params import PARAMS


def main():  # noqa: D103
    with ProcessPoolExecutor() as executor:
        for dt in list(
            get_times(p.stem for p in PARAMS.paths.contours.glob(f"{DAY}*.h5"))
        ):
            submit_nb_process(
                executor=executor,
                nb="find_contours",
                name="contours",
                params={
                    "FRAMES": None,
                    "COMPARE_WITH_TRACKPY": False,
                    "TIME": dt.isoformat(),
                },
            )


if __name__ == "__main__":
    main()
