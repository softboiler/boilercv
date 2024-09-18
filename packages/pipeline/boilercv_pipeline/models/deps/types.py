"""Types."""

from typing import NamedTuple, TypeAlias


class Slicer(NamedTuple):
    """Tuple of slice elements."""

    start: int | None
    stop: int | None
    step: int


Slicers: TypeAlias = dict[str, Slicer]
