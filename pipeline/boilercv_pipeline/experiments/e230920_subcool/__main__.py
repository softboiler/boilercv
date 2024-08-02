"""Subcooled bubble collapse experiment."""

from concurrent.futures import ProcessPoolExecutor

from boilercore.paths import fold, modified
from ploomber_engine import execute_notebook

from boilercv_pipeline.experiments.e230920_subcool import EXP, EXP_DATA, get_times
from boilercv_pipeline.models.params import PARAMS


def main():  # noqa: D103
    find_collapse = fold(
        PARAMS.package_paths.stages[f"experiments_{EXP}_find_collapse"]
    )
    if not modified(find_collapse):
        return
    execute_notebook(
        input_path=fold(
            PARAMS.package_paths.stages[f"experiments_{EXP}_get_thermal_data"]
        ),
        output_path=None,
    )
    with ProcessPoolExecutor() as executor:
        for dt in get_times(path.stem for path in EXP_DATA.iterdir()):
            executor.submit(
                execute_notebook,
                input_path=find_collapse,
                output_path=None,
                parameters={"TIME": dt.isoformat()},
            )


main()
