from pathlib import Path
from typing import Annotated as Ann

from cappa.arg import Arg
from cappa.base import command
from pydantic import Field

from boilercv_pipeline.models import stage
from boilercv_pipeline.models.params import Params
from boilercv_pipeline.models.path import DataDir, DirectoryPathSerPosix
from boilercv_pipeline.models.paths import paths


class Deps(stage.Deps):
    stage: DirectoryPathSerPosix = Path(__file__).parent
    hierarchical_data: DataDir = paths.hierarchical_data


class Outs(stage.Outs):
    contours: DataDir = paths.contours
    notes: DataDir = paths.notes
    cines: DataDir = paths.cines
    sheets: DataDir = paths.sheets


@command(
    default_long=True, invoke="boilercv_pipeline.manual.flatten_data_dir.__main__.main"
)
class FlattenDataDir(Params[Deps, Outs]):
    """Flatten the data directory structure.

    Directory structure looks like

        data
        └───YYYY-MM-DD
            ├───data
            ├───notes
            └───video
    """

    deps: Ann[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Ann[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
