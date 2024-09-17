from typing import Annotated as Ann

from cappa.arg import Arg
from cappa.base import command
from pydantic import Field

from boilercv_pipeline.models import stage
from boilercv_pipeline.models.params import Params
from boilercv_pipeline.models.path import DataDir
from boilercv_pipeline.models.paths import paths


class Deps(stage.Deps): ...


class Outs(stage.Outs):
    cines: DataDir = paths.cines


@command(default_long=True, invoke="boilercv_pipeline.stages.skip_cloud.__main__.main")
class SkipCloud(Params[Deps, Outs]):
    """The outs of this stage are too large and unwieldy to cache or push to cloud storage."""

    deps: Ann[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    outs: Ann[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
