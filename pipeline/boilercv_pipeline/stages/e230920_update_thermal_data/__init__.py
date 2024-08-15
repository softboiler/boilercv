from pathlib import Path
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command
from pydantic import BaseModel, DirectoryPath, Field

from boilercv_pipeline.models.paths import StagePaths, paths


class Deps(StagePaths):
    stage: DirectoryPath = Path(__file__).parent
    e230920_thermal_raw: Path = paths.e230920_thermal_raw


class Outs(StagePaths):
    e230920_thermal: Path = paths.e230920_thermal


@command(
    default_long=True,
    invoke="boilercv_pipeline.stages.e230920_update_thermal_data.__main__.main",
)
class E230920UpdateThermalData(BaseModel):
    """Update thermal data for the experiment."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
