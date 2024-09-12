from pathlib import Path
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command
from pydantic import Field

from boilercv_pipeline.models import stage
from boilercv_pipeline.models.params import Params
from boilercv_pipeline.models.path import DataDir, DirectoryPathSerPosix
from boilercv_pipeline.models.paths import paths


class Deps(stage.Deps):
    stage: DirectoryPathSerPosix = Path(__file__).parent
    sources: DataDir = paths.sources
    rois: DataDir = paths.rois
    contours: DataDir = paths.contours


class Outs(stage.Outs):
    filled: DataDir = paths.filled


@command(default_long=True, invoke="boilercv_pipeline.stages.fill.__main__.main")
class Fill(Params[Deps, Outs]):
    """Fill bubble contours."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
