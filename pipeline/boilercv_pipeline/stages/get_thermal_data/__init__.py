from pathlib import Path
from typing import Annotated as Ann
from typing import Self

from boilercore.fits import Fit
from cappa.arg import Arg
from cappa.base import command
from matplotlib.figure import Figure
from pandas import DataFrame
from pydantic import Field, model_validator

from boilercv_pipeline.models import data
from boilercv_pipeline.models.column import Col, Kind
from boilercv_pipeline.models.columns import Cols
from boilercv_pipeline.models.deps import DirSlicer
from boilercv_pipeline.models.params import Format
from boilercv_pipeline.models.path import (
    DataDir,
    DataFile,
    DirectoryPathSerPosix,
    DocsFile,
)
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.stage import DataStage as D  # noqa: N814
from boilercv_pipeline.models.stage import StagePaths
from boilercv_pipeline.models.subcool import Params, const


class Deps(StagePaths):
    stage: DirectoryPathSerPosix = Path(__file__).parent
    nb: DocsFile = paths.notebooks[stage.stem]
    thermal: DataDir = paths.thermal
    modelfunctions: DataDir = paths.modelfunctions

    @property
    def thermal_paths(self) -> list[Path]:
        return DirSlicer(
            path=self.thermal, include_patterns=const.include_patterns
        ).paths


class Outs(StagePaths):
    df: DataFile = paths.e230920_thermal
    plots: DataDir = paths.e230920_thermal_plots


class Dfs(data.types.Dfs):
    resampled: DataFrame = Field(default_factory=DataFrame)


class Plots(data.types.Plots):
    """Plots."""

    subcool_superheat: Figure = Field(default_factory=Figure)
    subcool: Figure = Field(default_factory=Figure)
    superheat: Figure = Field(default_factory=Figure)


class Data(data.Data[Dfs, Plots]):
    """Stage data."""

    dfs: Dfs = Field(default_factory=Dfs)
    plots: Plots = Field(default_factory=Plots)


class ThermalCols(Cols):
    """Thermal columns."""

    time: Ann[Col, Kind.idx, D.src, D.dst] = Col("time", "Time")
    time_elapsed: Ann[Col, D.dst] = Col("t", unit="s")
    time_elapsed_min: Ann[Col, D.dst] = Col("t", unit="s", dst_unit="min", scale=1 / 60)
    water_temps: Ann[list[Col], D.src, D.dst] = [
        Col("Tw3cal (C)", "T_w3"),
        Col("Tw4cal (C)", "T_w4"),
    ]

    water_temp: Ann[Col, D.dst] = Col("T_w (C)")
    superheat: Ann[Col, D.dst] = Col("ΔT_super (K)")
    subcool: Ann[Col, D.dst] = Col("ΔT_sub (K)")

    base_temp: Ann[Col, D.src, D.dst] = Col("T0cal (C)", "T_0")
    sample_temps: Ann[list[Col], D.src, D.dst] = [
        Col("T1cal (C)", "T_1"),
        Col("T2cal (C)", "T_2"),
        Col("T3cal (C)", "T_3"),
        Col("T4cal (C)", "T_4"),
        Col("T5cal (C)", "T_5"),
    ]
    surface_temp: Ann[Col, D.src, D.dst] = Col("T_s (C)")

    flux: Ann[Col, D.dst] = Col("q'' (W/cm^2)", scale=1e-4)
    boiling: Ann[Col, D.dst] = Col("T_sat (C)")
    video: Ann[Col, D.dst] = Col("Video")

    @model_validator(mode="after")
    def validate_time(self) -> Self:
        """Validate time column."""
        if len(self.idx) > 1 or self.time != self.idx[0]:
            raise ValueError("Expected only one index column.")
        return self


@command(
    default_long=True, invoke="boilercv_pipeline.stages.get_thermal_data.__main__.main"
)
class GetThermalData(Params[Deps, Outs, Data]):
    """Update thermal data for the experiment."""

    deps: Ann[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    """Stage dependencies."""
    outs: Ann[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
    """Stage outputs."""
    data: Ann[Data, Arg(hidden=True)] = Field(default_factory=Data, exclude=True)
    """Stage data."""
    cols: Ann[ThermalCols, Arg(hidden=True)] = Field(default_factory=ThermalCols)
    """Columns."""
    format: Ann[Format, Arg(hidden=True)] = Format(
        precision=3  # ? Suitable for integer-dominated temperatures
    )
    """Format parameters."""
    fit: Fit = Field(default_factory=Fit, exclude=True)
    """Model fit."""
    load_src_from_outs: bool = False
    """Load source columns from outputs."""
