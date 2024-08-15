from boilercore.notebooks.namespaces import get_nb_ns
from cappa.base import invoke

from boilercv_pipeline.stages.common.e230920 import read_nb
from boilercv_pipeline.stages.e230920_update_thermal_data import (
    E230920UpdateThermalData,
)


def main(args: E230920UpdateThermalData):
    get_nb_ns(
        nb=read_nb("e230920_update_thermal_data"), attributes=["data"]
    ).data.to_hdf(args.outs.e230920_thermal, key="thermal", complib="zlib", complevel=9)


if __name__ == "__main__":
    invoke(E230920UpdateThermalData)
