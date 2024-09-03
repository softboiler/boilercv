"""Types."""

from typing import TypeAlias

Slicer: TypeAlias = tuple[int | None, ...]
Slicers: TypeAlias = dict[str, Slicer]
