"""Pipeline types."""

from typing import TypeAlias

Slicer: TypeAlias = tuple[int, int]
Slicer2D: TypeAlias = tuple[Slicer, Slicer]
