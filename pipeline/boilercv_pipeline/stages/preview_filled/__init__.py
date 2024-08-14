from pathlib import Path
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command
from pydantic import DirectoryPath, Field

from boilercv_pipeline.contexts import ContextsMergeModel
from boilercv_pipeline.models.paths import DataDir, DataFile, MatchedPaths, paths


class Deps(MatchedPaths):
    stage: DirectoryPath = Path(__file__).parent
    filled: DataDir = paths.filled


class Outs(MatchedPaths):
    filled_preview: DataFile = paths.filled_preview


@command(
    default_long=True, invoke="boilercv_pipeline.stages.previe_filled.__main__.main"
)
class PreviewFilled(ContextsMergeModel):
    """Update previews for the filled contours stage."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
