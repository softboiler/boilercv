"""Contexts."""

from pathlib import Path
from typing import Any, NotRequired

from context_models.types import Context
from pydantic import BaseModel, Field

from boilercv_pipeline.config import const
from boilercv_pipeline.models.contexts.types import Kinds
from boilercv_pipeline.models.dvc import DvcYamlModel, Stage

BOILERCV_PIPELINE = "boilercv_pipeline"
"""Context name for `boilercv_pipeline`."""
DVC = "boilercv_dvc"
"""DVC context name for `boilercv_pipeline`."""
MODEL = "model"
"""DVC model attribute name."""
PARAMS = "params"
"""DVC params attribute name."""


class Roots(BaseModel):
    """Root directories."""

    data: Path | None = None
    """Data."""
    docs: Path | None = None
    """Docs."""


ROOTED = Roots(data=const.root / const.data, docs=const.root / const.docs)
"""Paths rooted to their directories."""


class DvcContext(BaseModel):
    """DVC context."""

    model: DvcYamlModel = Field(default_factory=DvcYamlModel)
    """Synchronized `dvc.yaml` configuration."""
    params: dict[str, Any] = Field(default_factory=dict)
    """DVC `params.yaml` synchronized to `dvc.yaml`."""
    stage: Stage = Field(default_factory=lambda: Stage(cmd=""))
    """Current stage."""


class BoilercvPipelineContext(BaseModel):
    """Root directory context."""

    roots: Roots = Field(default_factory=Roots)
    """Root directories for different kinds of paths."""
    kinds: Kinds = Field(default_factory=dict)
    """Kind of each path."""
    track_kinds: bool = False
    """Whether to track kinds."""


class BoilercvPipelineContexts(Context):
    """Boilercv pipeline context."""

    boilercv_pipeline: BoilercvPipelineContext
    boilercv_dvc: NotRequired[DvcContext]
