from pathlib import Path
from typing import Annotated

from boilercore.models import DefaultPathsModel
from cappa.arg import Arg
from cappa.base import command
from pydantic import BaseModel, Field

from boilercv_pipeline import get_parser
from boilercv_pipeline.models.config import default


class Params(BaseModel):
    """Stage parameters."""


class Deps(DefaultPathsModel):
    """Stage dependencies."""

    root: Path = Field(default=default.paths.root, exclude=True)
    hierarchical_data: Path = default.paths.hierarchical_data
    notes: Path = default.paths.notes
    cines: Path = default.paths.cines
    sheets: Path = default.paths.sheets


class Outs(DefaultPathsModel):
    """Stage outputs."""

    root: Path = Field(default=default.paths.root, exclude=True)
    notes: Path = default.paths.notes
    cines: Path = default.paths.cines
    sheets: Path = default.paths.sheets


@command(invoke="boilercv_pipeline.stages.flatten_data_dir.main", default_long=True)
class FlattenDataDir(BaseModel):
    params: Annotated[Params, Arg(parse=get_parser(Params))] = Params()
    deps: Annotated[Deps, Arg(parse=get_parser(Deps))] = Deps()
    outs: Annotated[Outs, Arg(parse=get_parser(Outs))] = Outs()
