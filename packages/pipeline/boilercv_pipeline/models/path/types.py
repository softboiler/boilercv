"""Types."""

from typing import Annotated as Ann
from typing import Literal, TypeAlias

from cappa.arg import Arg

from boilercv_pipeline.models.contexts import BoilercvPipelineContexts

Key: TypeAlias = Literal["data", "docs"]
"""Data or docs key."""
HiddenContext: TypeAlias = Ann[BoilercvPipelineContexts, Arg(hidden=True)]
"""Pipeline context as a hidden argument."""
