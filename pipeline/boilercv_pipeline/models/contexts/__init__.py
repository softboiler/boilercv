"""Contexts."""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from boilercv.contexts.types import Context
from boilercv_pipeline.config import const
from boilercv_pipeline.models.contexts.types import Kinds
from boilercv_pipeline.models.dvc import DvcYamlModel

BOILERCV_PIPELINE = "boilercv_pipeline"


class Roots(BaseModel):
    """Root directories."""

    data: Path | None = None
    """Data."""
    docs: Path | None = None
    """Docs."""


ROOTED = Roots(data=const.data, docs=const.docs)
"""Paths rooted to their directories."""


class BoilercvPipelineCtx(BaseModel):
    """Root directory context."""

    roots: Roots = Field(default_factory=Roots)
    """Root directories for different kinds of paths."""
    kinds: Kinds = Field(default_factory=dict)
    """Kind of each path."""
    track_kinds: bool = False
    """Whether to track kinds."""
    sync_dvc: bool = False
    """Whether to synchronize `dvc.yaml` configuration."""
    stages: list[str] = Field(default_factory=list)
    """Encountered stages."""
    dvc: DvcYamlModel = Field(default_factory=DvcYamlModel)
    """Synchronized `dvc.yaml` configuration."""
    dvc_params: dict[str, Any] = Field(default_factory=dict)
    """DVC `params.yaml` synchronized to `dvc.yaml`."""


class BoilercvPipelineCtxDict(Context):
    """Boilercv pipeline context."""

    boilercv_pipeline: BoilercvPipelineCtx
