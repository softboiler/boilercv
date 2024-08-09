from pathlib import Path
from typing import Annotated

from boilercore.models import DefaultPathsModel
from cappa.arg import Arg
from cappa.base import command
from pydantic import BaseModel, Field

from boilercv_pipeline.models import get_parser
from boilercv_pipeline.models.config import default


class Params(BaseModel):
    """Stage parameters."""


class Deps(DefaultPathsModel):
    """Stage dependencies."""

    root: Path = Field(default=default.paths.root, exclude=True)
    e230920_objects: Path = default.paths.e230920_objects


class Outs(DefaultPathsModel):
    """Stage outputs."""

    root: Path = Field(default=default.paths.root, exclude=True)
    e230920_tracks: Path = default.paths.e230920_tracks


@command(invoke="boilercv_pipeline.stages.e230920_find_tracks.main", default_long=True)
class E230920FindTracks(BaseModel):
    params: Annotated[Params, Arg(parse=get_parser(Params))] = Params()
    deps: Annotated[Deps, Arg(parse=get_parser(Deps))] = Deps()
    outs: Annotated[Outs, Arg(parse=get_parser(Outs))] = Outs()
