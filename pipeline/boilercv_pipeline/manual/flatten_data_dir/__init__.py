from pathlib import Path
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command
from pydantic import DirectoryPath, Field

from boilercv_pipeline.context import ContextModel
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.paths.types import StagePaths
from boilercv_pipeline.models.types.runtime import DataDir


class Deps(StagePaths):
    stage: DirectoryPath = Path(__file__).parent
    hierarchical_data: DataDir = paths.hierarchical_data


class Outs(StagePaths):
    contours: DataDir = paths.contours
    notes: DataDir = paths.notes
    cines: DataDir = paths.cines
    sheets: DataDir = paths.sheets


@command(
    default_long=True, invoke="boilercv_pipeline.manual.flatten_data_dir.__main__.main"
)
class FlattenDataDir(ContextModel):
    """Flatten the data directory structure.

    Directory structure looks like

        data
        └───YYYY-MM-DD
            ├───data
            ├───notes
            └───video
    """

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
