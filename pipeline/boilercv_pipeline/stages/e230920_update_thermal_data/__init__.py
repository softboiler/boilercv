from pathlib import Path
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command
from pydantic import DirectoryPath, Field

from boilercv_pipeline.context import ContextMergeModel
from boilercv_pipeline.models.paths import StagePaths, paths
from boilercv_pipeline.models.types.runtime import DataFile


class Deps(StagePaths):
    stage: DirectoryPath = Path(__file__).parent
    e230920_thermal_raw: DataFile = paths.e230920_thermal_raw


class Outs(StagePaths):
    e230920_thermal: DataFile = paths.e230920_thermal


@command(
    default_long=True,
    invoke="boilercv_pipeline.stages.e230920_update_thermal_data.__main__.main",
)
class E230920UpdateThermalData(ContextMergeModel):
    """Update thermal data for the experiment."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
