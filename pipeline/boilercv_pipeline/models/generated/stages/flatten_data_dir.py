from pathlib import Path
from typing import Annotated

from boilercore.models import DefaultPathsModel
from cappa.arg import Arg
from cappa.base import command
from pydantic import BaseModel, Field

from boilercv_pipeline.models.config import default


class Params(BaseModel):
    """Stage parameters."""


class Deps(DefaultPathsModel):
    """Stage dependencies."""

    root: Path = Field(default=default.paths.root, exclude=True)
    hierarchical_data: Path = default.paths.hierarchical_data


class Outs(DefaultPathsModel):
    """Stage outputs."""

    root: Path = Field(default=default.paths.root, exclude=True)


@command(invoke="boilercv_pipeline.stages.flatten_data_dir.main")
class FlattenDataDir(BaseModel):
    params: Annotated[Params, Arg(long=True)] = Params()
    deps: Annotated[Deps, Arg(long=True)] = Deps()
    outs: Annotated[Outs, Arg(long=True)] = Outs()
