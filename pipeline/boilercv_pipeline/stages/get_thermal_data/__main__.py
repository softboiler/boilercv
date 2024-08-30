from cappa.base import invoke

from boilercv_pipeline.stages.common.e230920 import apply_to_nb
from boilercv_pipeline.stages.get_thermal_data import GetThermalData as Params


def main(params: Params):
    apply_to_nb(params=params, nb=params.deps.nb.read_text(encoding="utf-8")).df.to_hdf(
        params.outs.dfs, key="thermal", complib="zlib", complevel=9
    )


if __name__ == "__main__":
    invoke(Params)
