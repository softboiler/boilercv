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
    large_sources: Path = default.paths.large_sources


class Outs(DefaultPathsModel):
    """Stage outputs."""

    root: Path = Field(default=default.paths.root, exclude=True)
    sources: Path = default.paths.sources
    rois: Path = default.paths.rois


@command(invoke="boilercv_pipeline.stages.binarize.main")
class Binarize(BaseModel):
    params: Annotated[Params, Arg(long=True)] = Params()
    deps: Annotated[Deps, Arg(long=True)] = Deps()
    outs: Annotated[Outs, Arg(long=True)] = Outs()
