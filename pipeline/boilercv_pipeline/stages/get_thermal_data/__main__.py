from cappa.base import invoke

from boilercv_pipeline.stages.common.e230920 import (
    apply_to_nb,
    df_to_compressed_hdf,
    save_plots,
)
from boilercv_pipeline.stages.get_thermal_data import GetThermalData as Params


def main(params: Params):
    outs = apply_to_nb(params=params, nb=params.deps.nb.read_text(encoding="utf-8"))
    df_to_compressed_hdf(outs.df, params.outs.df)
    save_plots(outs.plots, params.outs.plots)


if __name__ == "__main__":
    invoke(Params)
