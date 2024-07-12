"""Get mean absolute error of tracks."""

from concurrent.futures import ProcessPoolExecutor

from boilercv_pipeline.experiments.e230920_subcool import EXP_TIMES, submit_nb_process


def main():  # noqa: D103
    with ProcessPoolExecutor() as executor:
        for dt in EXP_TIMES:
            submit_nb_process(
                executor=executor,
                nb="get_mae",
                name="mae",
                params={"TIME": dt.isoformat()},
            )


if __name__ == "__main__":
    main()
