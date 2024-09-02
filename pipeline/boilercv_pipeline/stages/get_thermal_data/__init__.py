from pathlib import Path
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command
from pydantic import Field

from boilercv_pipeline.models.deps import DirSlicer
from boilercv_pipeline.models.path import (
    DataDir,
    DataFile,
    DirectoryPathSerPosix,
    DocsFile,
)
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.paths.types import StagePaths
from boilercv_pipeline.models.stages import Format, Params
from boilercv_pipeline.stages.common.e230920 import const


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


@command(
    default_long=True, invoke="boilercv_pipeline.stages.get_thermal_data.__main__.main"
)
class GetThermalData(Params[Deps, Outs]):
    """Update thermal data for the experiment."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    """Stage dependencies."""
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
    """Stage outputs."""
    format: Format = Format(precision=3)
    """Format parameters."""
