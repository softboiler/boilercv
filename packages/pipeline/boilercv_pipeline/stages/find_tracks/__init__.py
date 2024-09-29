from functools import partial
from pathlib import Path
from tomllib import loads
from typing import Annotated as Ann
from typing import get_args

from cappa.arg import Arg
from cappa.base import command
from matplotlib.figure import Figure
from pandas import DataFrame
from pydantic import AfterValidator, Field

from boilercv.correlations import META_TOML
from boilercv.correlations.models import Metadata
from boilercv.correlations.types import Equation
from boilercv.pipelines.contexts import get_pipeline_context
from boilercv_pipeline.models import columns, data, stage
from boilercv_pipeline.models.column import Col, Kind, LinkedCol
from boilercv_pipeline.models.columns import get_cols
from boilercv_pipeline.models.path import (
    DataDir,
    DataFile,
    DirectoryPathSerPosix,
    DocsFile,
)
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.stage import DfsPlotsOuts
from boilercv_pipeline.models.subcool import (
    FilledDeps,
    FilledParams,
    validate_time_suffixed_paths,
)
from boilercv_pipeline.stages import find_objects


class Deps(FilledDeps):
    stage: DirectoryPathSerPosix = Path(__file__).parent
    nb: DocsFile = paths.notebooks[stage.stem]
    objects: DataDir = paths.objects
    thermal: DataFile = paths.e230920_thermal


class Outs(DfsPlotsOuts):
    dfs: DataDir = paths.tracks
    plots: DataDir = paths.tracks_plots


class Dfs(data.Dfs):
    tracks: DataFrame = Field(default_factory=DataFrame)
    """Raw tracks before filtering to valid bubbles actually departing the surface."""
    bubbles: DataFrame = Field(default_factory=DataFrame)
    """Valid bubbles departing the boiling surface."""
    beta: DataFrame = Field(default_factory=DataFrame)
    """Empirical correlations for dimensionless bubble diameter."""
    nusselt: DataFrame = Field(default_factory=DataFrame)
    """Empirical correlations for bubble Nusselt number."""
    beta_err: DataFrame = Field(default_factory=DataFrame)
    """Absolute error between data and dimensionless bubble diameter correlations."""
    nusselt_err: DataFrame = Field(default_factory=DataFrame)
    """Absolute error between data and bubble Nusselt number correlations."""


class Plots(data.Plots):
    bubbles: Figure = Field(default_factory=Figure)
    multi: Figure = Field(default_factory=Figure)
    beta: Figure = Field(default_factory=Figure)
    beta_err: Figure = Field(default_factory=Figure)
    nusselt_err: Figure = Field(default_factory=Figure)
    mae: Figure = Field(default_factory=Figure)


class Data(data.Data[Dfs, Plots]):
    dfs: Dfs = Field(default_factory=Dfs)
    plots: Plots = Field(default_factory=Plots)


class DataStage(stage.DataStage):
    tracks: str = "tracks"
    """Raw tracks before filtering to valid bubbles actually departing the surface."""
    bubbles: str = "bubbles"
    """Valid bubbles departing the boiling surface."""
    beta: str = "beta"
    """Empirical correlations for dimensionless bubble diameter."""
    nusselt: str = "nusselt"
    """Empirical correlations for bubble Nusselt number."""
    beta_err: str = "beta_err"
    """Absolute error between data and dimensionless bubble diameter correlations."""
    nusselt_err: str = "nusselt_err"
    """Absolute error between data and bubble Nusselt number correlations."""


D = DataStage()
OC = find_objects.Cols()


def convert_col(source: Col, unit: str, fmt: str = "") -> LinkedCol:
    return (
        LinkedCol(sym=source.no_unit.name, unit=unit, source=source, fmt=fmt)
        if fmt
        else LinkedCol(sym=source.no_unit.name, unit=unit, source=source)
    )


EQUATIONS = get_args(Equation)
META = Metadata.model_validate(
    obj=loads(META_TOML.read_text("utf-8") if META_TOML.exists() else ""),
    context=get_pipeline_context(Metadata.get_context()),
)


class Cols(columns.Cols):
    frame: Ann[LinkedCol, Kind.idx, D.src, D.tracks] = OC.frame
    contour: Ann[LinkedCol, Kind.idx, D.src, D.tracks] = OC.contour

    time_elapsed: Ann[Col, Kind.idx, D.tracks] = Col("t", "s")
    bub: Ann[
        LinkedCol, Kind.idx, D.src, D.tracks, D.bubbles, D.beta, D.nusselt, D.dst
    ] = LinkedCol("Bubble", fmt=".0f", source=Col("particle"))
    bub_visible_frames: Ann[Col, Kind.idx, D.tracks] = Col(
        "t", "frames", "b, vis", fmt=".0f"
    )
    bub_visible: Ann[LinkedCol, Kind.idx, D.tracks] = LinkedCol(
        "t", "s", "b, vis", source=bub_visible_frames
    )

    x: Ann[LinkedCol, D.tracks] = convert_col(OC.x, "m")
    y: Ann[LinkedCol, D.tracks] = convert_col(OC.y, "m")

    u: Ann[LinkedCol, D.tracks] = LinkedCol("u", "m/s", source=x)
    v: Ann[LinkedCol, D.tracks] = LinkedCol("v", "m/s", source=y)

    diameter: Ann[LinkedCol, D.tracks] = convert_col(OC.diameter, "m")
    radius_of_gyration: Ann[LinkedCol, D.tracks] = convert_col(
        OC.radius_of_gyration, "m"
    )
    distance: Ann[Col, D.tracks] = Col("z", "m")

    bub_time: Ann[Col, Kind.idx, D.bubbles] = Col("t", "s", "b")
    bub_lifetime: Ann[Col, Kind.idx, D.bubbles] = Col("t", "s", "b,tot")

    bub_t0: Ann[Col, Kind.idx, D.bubbles] = Col("t", "s", "b0")
    bub_d0: Ann[Col, D.bubbles] = Col("d", "m", "b0")
    bub_x0: Ann[Col, D.bubbles] = Col("x", "m", "b0")
    bub_y0: Ann[Col, D.bubbles] = Col("y", "m", "b0")
    bub_u0: Ann[Col, D.bubbles] = Col("u", "m/s", "b0")
    bub_v0: Ann[Col, D.bubbles] = Col("v", "m/s", "b0")

    max_diam: Ann[Col, D.bubbles] = Col("d", "m", "b,max")
    diam_rate_of_change: Ann[Col, D.bubbles] = Col(r"\dot{d}", "m/s", "b")

    bub_reynolds: Ann[Col, D.dst] = Col("Re", sub="b")
    bub_reynolds0: Ann[Col, D.dst] = Col("Re", sub="b0")
    bub_fourier: Ann[Col, D.beta, D.nusselt, D.beta_err, D.nusselt_err, D.dst] = Col(
        "Fo", sub="b"
    )
    bub_nusselt: Ann[Col, D.nusselt, D.dst] = Col("Nu", sub="c")
    bub_beta: Ann[Col, D.beta, D.dst] = Col("β")

    corr: dict[Equation, Ann[Col, D.beta, D.nusselt, D.beta_err, D.nusselt_err]] = {  # pyright: ignore[reportAssignmentType]
        name: Col.only_raw(meta.name)
        for name, meta in META.items()
        if name in EQUATIONS
    }

    @property
    def tracks(self) -> list[Col]:
        """All tracks columns."""
        return get_cols(self, D.tracks)

    @property
    def bubbles(self) -> list[Col]:
        """All bubbles columns."""
        return get_cols(self, D.bubbles)

    @property
    def corr_beta(self) -> list[Col]:
        """All dimensionless bubble diameter correlation columns."""
        return [*get_cols(self, D.beta), *self.corr.values()]

    @property
    def corr_nusselt(self) -> list[Col]:
        """All Nusselt number correlation columns."""
        return [*get_cols(self, D.nusselt), *self.corr.values()]

    @property
    def err_beta(self) -> list[Col]:
        """All dimensionless bubble diameter absolute error columns."""
        return [*get_cols(self, D.beta_err), *self.corr.values()]

    @property
    def err_nusselt(self) -> list[Col]:
        """All Nusselt number correlation absolute error columns."""
        return [*get_cols(self, D.nusselt_err), *self.corr.values()]


@command(invoke="boilercv_pipeline.stages.find_tracks.__main__.main", default_long=True)
class FindTracks(FilledParams[Deps, Outs, Data]):
    """Export all tracks for this experiment."""

    deps: Ann[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    """Stage dependencies."""
    outs: Ann[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
    """Stage outputs."""
    data: Ann[Data, Arg(hidden=True)] = Field(default_factory=Data, exclude=True)
    """Stage data."""
    cols: Ann[Cols, Arg(hidden=True)] = Field(default_factory=Cols)
    """Columns."""
    objects: Ann[
        list[Path],
        Arg(hidden=True),
        AfterValidator(
            partial(
                validate_time_suffixed_paths,
                times_field="times",
                paths_field="deps",
                paths_subfield="objects",
            )
        ),
    ] = Field(default_factory=list)
    """Paths to objects."""
