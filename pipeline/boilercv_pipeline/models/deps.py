"""Dependency models."""

from pathlib import Path
from re import search

from pydantic import BaseModel, Field

from boilercv_pipeline.models.types import Slicer, Slicers


def get_slices(slicers: Slicers) -> dict[str, slice]:
    """Get slices from slicers."""
    return {k: slice(*(v or (None,))) for k, v in slicers.items()}


def first_slicer(n: int | None, step: int = 1) -> Slicer:
    """Slicer for the first `n` elements taken at `step`s."""
    return (None, *[step * f for f in (n - 1, 1)]) if n else (None, None, step)


class DirSlicer(BaseModel):
    """Directory slicer."""

    path: Path
    include: list[str] = Field(default_factory=list)
    exclude: list[str] = Field(default_factory=list)
    include_patterns: list[str] = Field(default_factory=list)
    exclude_patterns: list[str] = Field(default_factory=list)
    slicers: dict[str, Slicers] = Field(default_factory=dict)
    slicer_patterns: dict[str, Slicers] = Field(default_factory=dict)

    @property
    def paths(self) -> list[Path]:
        """Filtered paths."""
        return [
            file
            for file in self.path.iterdir()
            if (not self.include or file.stem in self.include)
            and (file.stem not in self.exclude)
            and (
                not self.include_patterns
                or any(search(pat, file.stem) for pat in self.include_patterns)
            )
            and not any(search(pat, file.stem) for pat in self.exclude_patterns)
        ]


def get_slicers(
    path: Path,
    path_slicers: dict[str, Slicers] | None = None,
    slicer_patterns: dict[str, Slicers] | None = None,
) -> Slicers:
    """Get slicers for a path."""
    slicers: Slicers = {}
    if path_slicers:
        slicers = path_slicers.get(path.stem, slicers)
    if slicer_patterns:
        for pat, slicer in slicer_patterns.items():
            if search(pat, path.stem):
                slicers = slicer
                break
    return slicers
