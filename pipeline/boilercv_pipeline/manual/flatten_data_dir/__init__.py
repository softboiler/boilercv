from pathlib import Path
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command
from pydantic import DirectoryPath, Field

from boilercv_pipeline.contexts import ContextsMergeModel
from boilercv_pipeline.models.paths import DataDir, MatchedPaths, paths


class Deps(MatchedPaths):
    stage: DirectoryPath = Path(__file__).parent
    hierarchical_data: DataDir = paths.hierarchical_data


class Outs(MatchedPaths):
    contours: DataDir = paths.contours
    notes: DataDir = paths.notes
    cines: DataDir = paths.cines
    sheets: DataDir = paths.sheets


@command(
    default_long=True, invoke="boilercv_pipeline.stages.flatten_data_dir.__main__.main"
)
class FlattenDataDir(ContextsMergeModel):
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
