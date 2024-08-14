from pathlib import Path
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command
from pydantic import BaseModel, Field, FilePath

from boilercv_pipeline.models.paths import DataDir, MatchedPaths, paths


class Deps(MatchedPaths):
    stage: FilePath = Path(__file__)
    cines: DataDir = paths.cines


class Outs(MatchedPaths):
    large_sources: DataDir = paths.large_sources


@command(default_long=True, invoke="boilercv_pipeline.stages.convert.__main__.main")
class Convert(BaseModel):
    """Convert CINEs to NetCDF."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
