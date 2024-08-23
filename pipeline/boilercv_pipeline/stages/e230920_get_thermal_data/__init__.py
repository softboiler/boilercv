from pathlib import Path
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command
from pydantic import DirectoryPath, Field

from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.paths.types import StagePaths
from boilercv_pipeline.models.stages import Params
from boilercv_pipeline.models.types.runtime import DataFile, DocsFile


class Deps(StagePaths):
    stage: DirectoryPath = Path(__file__).parent
    nb: DocsFile = paths.notebooks[stage.stem]
    e230920_thermal_raw: DataFile = paths.e230920_thermal_raw


class Outs(StagePaths):
    e230920_thermal: DataFile = paths.e230920_thermal


@command(
    default_long=True,
    invoke="boilercv_pipeline.stages.e230920_get_thermal_data.__main__.main",
)
class E230920GetThermalData(Params[Deps, Outs]):
    """Update thermal data for the experiment."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
