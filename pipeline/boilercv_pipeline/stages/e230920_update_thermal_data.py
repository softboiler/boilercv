"""Update thermal data for the experiment."""

from boilercore.notebooks.namespaces import get_nb_ns

from boilercv_pipeline.stages.common.e230920 import EXP_DATA, read_nb


def main():  # noqa: D103
    get_nb_ns(nb=read_nb("get_thermal_data"), attributes=["data"]).data.to_hdf(
        EXP_DATA / "2023-09-20_thermal.h5", key="centers", complib="zlib", complevel=9
    )


if __name__ == "__main__":
    main()
