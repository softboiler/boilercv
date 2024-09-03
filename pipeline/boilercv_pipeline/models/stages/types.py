"""Types."""

from typing import TypeVar

from boilercv_pipeline.models.stage import StagePaths

Deps_T = TypeVar("Deps_T", bound=StagePaths, covariant=True)
"""Dependencies type."""
Outs_T = TypeVar("Outs_T", bound=StagePaths, covariant=True)
"""Outputs type."""
