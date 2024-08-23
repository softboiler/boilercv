"""Types."""

from pathlib import Path
from typing import Literal, TypeAlias, TypeVar

from pydantic import BaseModel

Model = TypeVar("Model", bound=BaseModel)
"""Model type."""
Kind = Literal["DataDir", "DataFile", "DocsDir", "DocsFile"]
"""File or directory kind."""
Kinds: TypeAlias = dict[Path, Kind]
"""Paths and their kinds."""
Slicer: TypeAlias = tuple[int | None, ...]
Slicers: TypeAlias = dict[str, Slicer]
