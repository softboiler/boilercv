"""Pipeline types."""

from typing import TypeAlias, TypeVar

T = TypeVar("T")
Slicer: TypeAlias = tuple[int, int]
Slicer2D: TypeAlias = tuple[Slicer, Slicer]
