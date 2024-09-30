from functools import partial
from pathlib import Path
from typing import Annotated as Ann

from cappa.arg import Arg
from cappa.base import command
from matplotlib.figure import Figure
from pandas import DataFrame
from pydantic import AfterValidator, Field

from boilercv.data import FRAME, PX, XPX, YPX, X, Y
from boilercv_pipeline.models import columns, data, stage
from boilercv_pipeline.models.column import Col, ConstCol, Kind, LinkedCol
from boilercv_pipeline.models.columns import get_cols
from boilercv_pipeline.models.path import DataDir, DirectoryPathSerPosix, DocsFile
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.stage import DfsPlotsOuts
from boilercv_pipeline.models.subcool import (
    FilledDeps,
    FilledParams,
    validate_time_suffixed_paths,
)
from boilercv_pipeline.parser import PairedArg


class Deps(FilledDeps):
    stage: DirectoryPathSerPosix = Path(__file__).parent
    nb: DocsFile = paths.notebooks[stage.stem]
    contours: DataDir = paths.contours


class Outs(DfsPlotsOuts):
    dfs: DataDir = paths.objects
    plots: DataDir = paths.objects_plots


class DataStage(stage.DataStage):
    trackpy: str = "trackpy"
    centroids: str = "centroids"
    geo: str = "geo"


D = DataStage()


class Dfs(data.Dfs):
    trackpy: DataFrame = Field(default_factory=DataFrame)
    centroids: DataFrame = Field(default_factory=DataFrame)
    geo: DataFrame = Field(default_factory=DataFrame)


class Plots(data.Plots):
    composite: Figure = Field(default_factory=Figure)


class Data(data.Data[Dfs, Plots]):
    dfs: Dfs = Field(default_factory=Dfs)
    plots: Plots = Field(default_factory=Plots)


class Cols(columns.Cols):
    frame: Ann[LinkedCol, Kind.idx, D.src, D.trackpy, D.dst] = LinkedCol(
        "Frame", fmt=".0f", source=Col(FRAME)
    )
    contour: Ann[LinkedCol, Kind.idx, D.src, D.dst] = LinkedCol(
        "Contour", fmt=".0f", source=Col("contour")
    )

    x: Ann[LinkedCol, D.src, D.dst] = LinkedCol(X, PX, source=Col(XPX))
    y: Ann[LinkedCol, D.src, D.dst] = LinkedCol(Y, PX, source=Col(YPX))
    x_tp: LinkedCol = LinkedCol(X, PX, source=Col(X))
    y_tp: LinkedCol = LinkedCol(Y, PX, source=Col(Y))

    size: Ann[LinkedCol, D.trackpy] = LinkedCol("Size", PX, source=Col("size"))

    centroid: Ann[Col, D.centroids] = Col("Centroid")

    geometry: Col = Col("Geometry")

    area: Ann[Col, D.geo, D.dst] = Col("A", "px^2")
    diameter: Ann[Col, D.geo, D.dst] = Col("d", PX)
    radius_of_gyration: Ann[Col, D.geo, D.dst] = Col("r", PX)

    approach_tp: ConstCol = ConstCol("Approach", val="Trackpy")
    approach: ConstCol = ConstCol("Approach", val="Centroids")

    @property
    def trackpy(self) -> list[LinkedCol]:
        """All TrackPy columns."""
        return get_cols(self, D.trackpy)  # pyright: ignore[reportReturnType]

    @property
    def centroids(self) -> list[Col]:
        """All centroids columns."""
        return [*self.get_indices(), *get_cols(self, D.centroids)]  # pyright: ignore[reportReturnType]

    @property
    def geo(self) -> list[Col]:
        """All geometry columns."""
        return [*self.get_indices(), *get_cols(self, D.geo)]  # pyright: ignore[reportReturnType]


@command(
    invoke="boilercv_pipeline.stages.find_objects.__main__.main", default_long=True
)
class FindObjects(FilledParams[Deps, Outs, Data]):
    """Find objects."""

    deps: Ann[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    """Stage dependencies."""
    outs: Ann[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
    """Stage outputs."""
    data: Ann[Data, Arg(hidden=True)] = Field(default_factory=Data, exclude=True)
    """Stage data."""
    cols: Ann[Cols, Arg(hidden=True)] = Field(default_factory=Cols)
    """Columns."""
    compare_with_trackpy: Ann[bool, PairedArg("compare_with_trackpy")] = False
    """Whether to get objects using the Trackpy approach."""
    guess_diameter: int = 21
    """Guess diameter for the Trackpy approach. (px)"""
    contours: Ann[
        list[Path],
        Arg(hidden=True),
        AfterValidator(
            partial(
                validate_time_suffixed_paths,
                times_field="times",
                paths_field="deps",
                paths_subfield="contours",
                subfield_prefix=False,
            )
        ),
    ] = Field(default_factory=list)
    """Paths to contours."""
