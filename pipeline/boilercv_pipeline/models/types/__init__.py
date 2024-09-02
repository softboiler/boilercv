"""Types."""

from typing import TypeAlias, TypeVar

from pydantic import BaseModel

Model = TypeVar("Model", bound=BaseModel)
"""Model type."""
Slicer: TypeAlias = tuple[int | None, ...]
Slicers: TypeAlias = dict[str, Slicer]
