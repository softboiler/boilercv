from pathlib import Path
from typing import Annotated as Ann

from cappa.arg import Arg
from cappa.base import command
from matplotlib.figure import Figure
from pandas import DataFrame
from pydantic import Field

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
    validate_deps_paths,
)
from boilercv_pipeline.stages import find_objects


class Deps(FilledDeps):
    stage: DirectoryPathSerPosix = Path(__file__).parent
    nb: DocsFile = paths.notebooks[stage.stem]
    objects: DataDir = paths.objects
    thermal: DataFile = paths.e230920_thermal
    filled: DataDir = paths.filled


class Outs(DfsPlotsOuts):
    dfs: DataDir = paths.tracks
    plots: DataDir = paths.tracks_plots


class Dfs(data.Dfs):
    tracks: DataFrame = Field(default_factory=DataFrame)
    bubbles: DataFrame = Field(default_factory=DataFrame)


class Plots(data.Plots):
    multi: Figure = Field(default_factory=Figure)
    corr: Figure = Field(default_factory=Figure)


class Data(data.Data[Dfs, Plots]):
    dfs: Dfs = Field(default_factory=Dfs)
    plots: Plots = Field(default_factory=Plots)


class DataStage(stage.DataStage):
    tracks: str = "tracks"
    bubbles: str = "bubbles"


D = DataStage()
OC = find_objects.Cols()


def convert_col(source: Col, unit: str, fmt: str = "") -> LinkedCol:
    return (
        LinkedCol(sym=source.no_unit.name, unit=unit, source=source, fmt=fmt)
        if fmt
        else LinkedCol(sym=source.no_unit.name, unit=unit, source=source)
    )


class Cols(columns.Cols):
    time_elapsed: Ann[Col, Kind.idx, D.tracks] = Col("t", "s")
    bubble: Ann[LinkedCol, Kind.idx, D.src, D.tracks] = LinkedCol(
        "Bubble", fmt=".0f", source=Col("particle")
    )
    bubble_visible_frames: Ann[Col, Kind.idx, D.tracks] = Col(
        "t", "frames", "b, vis", fmt=".0f"
    )
    bubble_visible: Ann[LinkedCol, Kind.idx, D.tracks] = LinkedCol(
        "t", "s", "b, vis", source=bubble_visible_frames
    )

    x: Ann[LinkedCol, D.tracks] = convert_col(OC.x, "m")
    y: Ann[LinkedCol, D.tracks] = convert_col(OC.y, "m")
    u: Ann[LinkedCol, D.tracks] = LinkedCol("u", "m/s", source=x)
    v: Ann[LinkedCol, D.tracks] = LinkedCol("v", "m/s", source=y)

    diameter: Ann[LinkedCol, D.tracks] = convert_col(OC.diameter, "m")
    radius_of_gyration: Ann[LinkedCol, D.tracks] = convert_col(
        OC.radius_of_gyration, "m"
    )
    distance: Ann[Col, D.tracks] = Col("d", "m")

    bubble_time: Ann[Col, Kind.idx, D.bubbles] = Col("t", "s", "b")
    bubble_lifetime: Ann[Col, Kind.idx, D.bubbles] = Col("t", "s", "b,tot")

    bubble_depart_t: Ann[Col, Kind.idx, D.bubbles] = Col("t", "s", "b0")
    bubble_depart_d: Ann[Col, D.bubbles] = Col("d", "m", "b0")
    bubble_depart_x: Ann[Col, D.bubbles] = Col("x", "m", "b0")
    bubble_depart_y: Ann[Col, D.bubbles] = Col("y", "m", "b0")
    bubble_depart_u: Ann[Col, D.bubbles] = Col("u", "m/s", "b0")
    bubble_depart_v: Ann[Col, D.bubbles] = Col("v", "m/s", "b0")

    max_diameter: Ann[Col, D.bubbles] = Col("d", "m", "b,max")
    diameter_rate_of_change: Ann[Col, D.bubbles] = Col(r"\dot{d}", "m/s", "b")

    @property
    def tracks(self) -> list[Col]:
        """All tracks columns."""
        return get_cols(self, D.tracks)

    @property
    def bubbles(self) -> list[Col]:
        """All bubbles columns."""
        return get_cols(self, D.bubbles)


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
    objects: Ann[list[Path], validate_deps_paths("objects")] = Field(
        default_factory=list
    )
    """Paths to objects."""
