from pathlib import Path
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command
from pydantic import DirectoryPath, Field

from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.paths.types import StagePaths
from boilercv_pipeline.models.stages import Params
from boilercv_pipeline.models.types.runtime import DataDir, DataFile


class Deps(StagePaths):
    stage: DirectoryPath = Path(__file__).parent
    sources: DataDir = paths.sources
    rois: DataDir = paths.rois


class Outs(StagePaths):
    binarized_preview: DataFile = paths.binarized_preview


@command(
    default_long=True, invoke="boilercv_pipeline.stages.preview_binarized.__main__.main"
)
class PreviewBinarized(Params[Deps, Outs]):
    """Update previews for the binarization stage."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)