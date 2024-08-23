from cappa.base import invoke

from boilercv_pipeline.stages.common.e230920 import apply_to_nb
from boilercv_pipeline.stages.e230920_get_thermal_data import E230920GetThermalData


def main(params: E230920GetThermalData):
    apply_to_nb(params=params, nb=params.deps.nb.read_text(encoding="utf-8")).df.to_hdf(
        params.outs.e230920_thermal, key="thermal", complib="zlib", complevel=9
    )


if __name__ == "__main__":
    invoke(E230920GetThermalData)
