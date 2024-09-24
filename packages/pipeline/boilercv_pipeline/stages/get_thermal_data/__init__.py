from pathlib import Path
from typing import Annotated as Ann

from boilercore.fits import Fit
from cappa.arg import Arg
from cappa.base import command
from matplotlib.figure import Figure
from pandas import DataFrame
from pydantic import Field

from boilercv_pipeline.models import columns, data, stage
from boilercv_pipeline.models.column import Col, IdentityCol, Kind, LinkedCol
from boilercv_pipeline.models.deps import DirSlicer
from boilercv_pipeline.models.path import (
    DataDir,
    DataFile,
    DirectoryPathSerPosix,
    DocsFile,
)
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.subcool import SubcoolParams, const
from boilercv_pipeline.parser import PairedArg


class Deps(stage.Deps):
    stage: DirectoryPathSerPosix = Path(__file__).parent
    nb: DocsFile = paths.notebooks[stage.stem]
    thermal: DataDir = paths.thermal
    modelfunctions: DataDir = paths.modelfunctions

    @property
    def thermal_paths(self) -> list[Path]:
        return DirSlicer(
            path=self.thermal, include_patterns=const.include_patterns
        ).paths


class Outs(stage.Outs):
    df: DataFile = paths.e230920_thermal
    plots: DataDir = paths.e230920_thermal_plots


class Dfs(data.Dfs):
    resampled: DataFrame = Field(default_factory=DataFrame)


class Plots(data.Plots):
    subcool_superheat: Figure = Field(default_factory=Figure)
    subcool: Figure = Field(default_factory=Figure)
    superheat: Figure = Field(default_factory=Figure)


class Data(data.Data[Dfs, Plots]):
    dfs: Dfs = Field(default_factory=Dfs)
    plots: Plots = Field(default_factory=Plots)


D = const.data_stage


class Cols(columns.Cols):
    time: Ann[LinkedCol, Kind.idx, D.src, D.dst] = LinkedCol("Time", source=Col("time"))
    time_elapsed: Ann[Col, D.dst] = Col("t", "s")
    time_elapsed_min: Ann[LinkedCol, D.dst] = LinkedCol("t", "min", source=time_elapsed)
    water_temps: Ann[list[LinkedCol], D.src, D.dst] = [
        LinkedCol(dst, "C", source=Col(src, "C"))
        for src, dst in {"Tw3cal": "T_w3", "Tw4cal": "T_w4"}.items()
    ]
    water_temp: Ann[LinkedCol, D.dst] = LinkedCol("T_w", "C")
    superheat: Ann[LinkedCol, D.dst] = LinkedCol("ΔT_super", "K")
    subcool: Ann[LinkedCol, D.dst] = LinkedCol("ΔT_sub", "K")

    sample_temps: Ann[list[LinkedCol], D.src, D.dst] = [
        LinkedCol(dst, "C", source=Col(src, "C"))
        for src, dst in {
            "T1cal": "T_1",
            "T2cal": "T_2",
            "T3cal": "T_3",
            "T4cal": "T_4",
            "T5cal": "T_5",
        }.items()
    ]
    surface_temp: Ann[IdentityCol, D.src, D.dst] = IdentityCol("T_s (C)")
    flux: Ann[LinkedCol, D.dst] = LinkedCol("q''", "W/cm^2", source=Col("q''", "W/m^2"))
    boiling: Ann[Col, D.dst] = Col("T_sat (C)")
    video: Ann[Col, D.dst] = Col("Video")


@command(
    default_long=True, invoke="boilercv_pipeline.stages.get_thermal_data.__main__.main"
)
class GetThermalData(SubcoolParams[Deps, Outs, Data]):
    """Update thermal data for the experiment."""

    deps: Ann[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    """Stage dependencies."""
    outs: Ann[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
    """Stage outputs."""
    data: Ann[Data, Arg(hidden=True)] = Field(default_factory=Data, exclude=True)
    """Stage data."""
    cols: Ann[Cols, Arg(hidden=True)] = Field(default_factory=Cols)
    """Columns."""
    fit: Fit = Field(default_factory=Fit, exclude=True)
    """Model fit."""
    load_src_from_outs: Ann[bool, PairedArg("load_src_from_outs")] = False
    """Load source columns from outputs."""
