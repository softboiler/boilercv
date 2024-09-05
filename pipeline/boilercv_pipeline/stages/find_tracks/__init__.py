from pathlib import Path
from typing import Annotated as Ann

from cappa.arg import Arg
from cappa.base import command
from pydantic import Field

from boilercv_pipeline.models import columns, data, stage
from boilercv_pipeline.models.deps.types import Slicers
from boilercv_pipeline.models.path import DataDir, DirectoryPathSerPosix, DocsFile
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.stage import DfsPlotsOuts
from boilercv_pipeline.models.subcool import (
    FilledDeps,
    FilledParams,
    validate_deps_paths,
)


class Deps(FilledDeps):
    stage: DirectoryPathSerPosix = Path(__file__).parent
    nb: DocsFile = paths.notebooks[stage.stem]
    objects: DataDir = paths.objects
    filled: DataDir = paths.filled


class Outs(DfsPlotsOuts):
    dfs: DataDir = paths.tracks
    plots: DataDir = paths.tracks_plots


class DataStage(stage.DataStage):
    src: str = "src"
    trackpy: str = "trackpy"
    centroids: str = "centroids"
    geo: str = "geo"
    dst: str = "dst"


D = DataStage()
"""Data stage in a pipeline stage."""


class Dfs(data.types.Dfs): ...


class Plots(data.types.Plots): ...


class Data(data.Data[Dfs, Plots]):
    dfs: Dfs = Field(default_factory=Dfs)
    plots: Plots = Field(default_factory=Plots)


class Cols(columns.Cols): ...


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
    slicer_patterns: dict[str, Slicers] = Field(default_factory=dict)
    """Slicer patterns."""
    objects: Ann[list[Path], validate_deps_paths("objects")] = Field(
        default_factory=list
    )
    """Paths to objects."""
