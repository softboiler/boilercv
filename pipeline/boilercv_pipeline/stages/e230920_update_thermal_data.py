"""Update thermal data for the experiment."""

from boilercore.notebooks.namespaces import get_nb_ns
from cappa.base import invoke

from boilercv_pipeline.models.generated.stages.e230920_update_thermal_data import (
    E230920UpdateThermalData,
)
from boilercv_pipeline.stages.common.e230920 import read_nb


def main(args: E230920UpdateThermalData):  # noqa: D103
    get_nb_ns(
        nb=read_nb("e230920_update_thermal_data"), attributes=["data"]
    ).data.to_hdf(args.outs.e230920_thermal, key="thermal", complib="zlib", complevel=9)


if __name__ == "__main__":
    invoke(E230920UpdateThermalData)
