from typing import Annotated

from cappa.arg import Arg
from cappa.base import command
from pydantic import Field

from boilercv_pipeline.models.params import Params
from boilercv_pipeline.models.path import DataDir
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.stage import StagePaths


class Deps(StagePaths): ...


class Outs(StagePaths):
    cines: DataDir = paths.cines


@command(default_long=True, invoke="boilercv_pipeline.stages.skip_cloud.__main__.main")
class SkipCloud(Params[Deps, Outs]):
    """The outs of this stage are too large and unwieldy to cache or push to cloud storage."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
