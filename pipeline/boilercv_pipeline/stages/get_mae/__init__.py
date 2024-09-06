from pathlib import Path
from typing import Annotated as Ann

from cappa.arg import Arg
from cappa.base import command
from pydantic import Field

from boilercv_pipeline.models import columns, data, stage
from boilercv_pipeline.models.path import (
    DataDir,
    DataFile,
    DirectoryPathSerPosix,
    DocsFile,
)
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.stage import DfsPlotsOuts, StagePaths
from boilercv_pipeline.models.subcool import (
    SubcoolParams,
    validate_deps_paths,
    validate_outs_paths,
)
from boilercv_pipeline.stages import find_tracks


class Deps(StagePaths):
    stage: DirectoryPathSerPosix = Path(__file__).parent
    nb: DocsFile = paths.notebooks[stage.stem]
    thermal: DataFile = paths.e230920_thermal
    tracks: DataDir = paths.tracks


class Outs(DfsPlotsOuts):
    dfs: DataDir = paths.mae
    plots: DataDir = paths.mae_plots


class Dfs(data.Dfs): ...


class Plots(data.Plots): ...


class Data(data.Data[Dfs, Plots]):
    dfs: Dfs = Field(default_factory=Dfs)
    plots: Plots = Field(default_factory=Plots)


class DataStage(stage.DataStage): ...


D = DataStage()
TC = find_tracks.Cols()


class Cols(columns.Cols): ...


@command(invoke="boilercv_pipeline.stages.get_mae.__main__.main", default_long=True)
class GetMae(SubcoolParams[Deps, Outs, Data]):
    """Export all tracks for this experiment."""

    deps: Ann[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    """Stage dependencies."""
    outs: Ann[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
    """Stage outputs."""
    data: Ann[Data, Arg(hidden=True)] = Field(default_factory=Data, exclude=True)
    """Stage data."""
    cols: Ann[Cols, Arg(hidden=True)] = Field(default_factory=Cols)
    """Columns."""
    tracks: Ann[list[Path], validate_deps_paths("tracks")] = Field(default_factory=list)
    """Paths to tracks."""
    dfs: Ann[list[Path], validate_outs_paths("dfs")] = Field(default_factory=list)
    """Paths to data frame stage outputs."""
