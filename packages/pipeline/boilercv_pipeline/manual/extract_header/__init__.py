from pathlib import Path
from typing import Annotated as Ann

from boilercv_pipeline.models import stage
from boilercv_pipeline.models.params import Params
from boilercv_pipeline.models.path import DataDir, DirectoryPathSerPosix
from boilercv_pipeline.models.paths import paths
from cappa.arg import Arg
from cappa.base import command
from pydantic import Field


class Deps(stage.Deps):
    stage: DirectoryPathSerPosix = Path(__file__).parent
    sources: DataDir = paths.sources


class Outs(stage.Outs):
    headers: DataDir = paths.headers


@command(
    default_long=True, invoke="boilercv_pipeline.manual.extract_header.__main__.main"
)
class ExtractHeader(Params[Deps, Outs]):
    """Extract headers from videos."""

    deps: Ann[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Ann[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
