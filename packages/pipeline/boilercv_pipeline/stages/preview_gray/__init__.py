from pathlib import Path
from typing import Annotated as Ann

from cappa.arg import Arg
from cappa.base import command
from pydantic import Field

from boilercv_pipeline.models import stage
from boilercv_pipeline.models.params import Params
from boilercv_pipeline.models.path import DataDir, DataFile, DirectoryPathSerPosix
from boilercv_pipeline.models.paths import paths


class Deps(stage.Deps):
    stage: DirectoryPathSerPosix = Path(__file__).parent
    large_sources: DataDir = paths.large_sources


class Outs(stage.Outs):
    gray_preview: DataFile = paths.gray_preview


@command(
    default_long=True, invoke="boilercv_pipeline.stages.preview_gray.__main__.main"
)
class PreviewGray(Params[Deps, Outs]):
    """Update previews for grayscale videos."""

    deps: Ann[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Ann[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
