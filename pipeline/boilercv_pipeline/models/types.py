"""Types."""

from pathlib import Path
from typing import Literal, TypeVar

from pydantic import BaseModel

from boilercv_pipeline.contexts.types import Contexts

Model = TypeVar("Model", bound=BaseModel)
"""Model type."""
Kind = Literal["DataDir", "DataFile", "DocsDir", "DocsFile", "other"]
"""File or directory kind."""


class Roots(BaseModel):
    """Root directories."""

    data: Path | None = None
    docs: Path | None = None


class RootContexts(Contexts):
    """Root directory contexts."""

    roots: Roots
