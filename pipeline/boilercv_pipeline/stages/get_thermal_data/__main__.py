from cappa.base import invoke

from boilercv_pipeline.dfs import save_df
from boilercv_pipeline.nbs import apply_to_nb
from boilercv_pipeline.plotting import save_plots
from boilercv_pipeline.stages.get_thermal_data import GetThermalData as Params


def main(params: Params):
    data = apply_to_nb(params=params, nb=params.deps.nb.read_text(encoding="utf-8"))
    save_df(data.dfs.dst, params.outs.df)
    save_plots(data.plots, params.outs.plots)


if __name__ == "__main__":
    invoke(Params)
