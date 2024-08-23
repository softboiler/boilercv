"""Dependency models."""

from functools import cached_property
from pathlib import Path
from re import Pattern, compile

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

    @cached_property
    def include_patterns_(self) -> list[Pattern[str]]:
        """Compiled include patterns."""
        return [compile(pat) for pat in self.include_patterns]

    @cached_property
    def exclude_patterns_(self) -> list[Pattern[str]]:
        """Compiled exclude patterns."""
        return [compile(pat) for pat in self.exclude_patterns]

    @cached_property
    def slice_patterns_(self) -> dict[Pattern[str], Slicers]:
        """Compiled exclude patterns."""
        return {compile(pat): slice_ for pat, slice_ in self.slicer_patterns.items()}

    @cached_property
    def paths(self) -> list[Path]:
        """Filtered paths."""
        return [
            file
            for file in self.path.iterdir()
            if (not self.include or file.stem in self.include)
            and (file.stem not in self.exclude)
            and (
                not self.include_patterns
                or any(pat.search(file.stem) for pat in self.include_patterns_)
            )
            and not any(pat.search(file.stem) for pat in self.exclude_patterns_)
        ]

    @cached_property
    def path_slicers(self) -> dict[Path, Slicers]:
        """Slicers for paths."""
        path_slicers = {}
        for file in self.paths:
            slicers: Slicers = {}
            if self.slicers:
                slicers = self.slicers.get(file.stem, slicers)
            if self.slicer_patterns:
                for pat, slicer in self.slice_patterns_.items():
                    if pat.search(file.stem):
                        slicers = slicer
                        break
            path_slicers[file] = slicers
        return path_slicers

    @cached_property
    def path_slices(self) -> dict[Path, dict[str, slice]]:
        """Slices for paths."""
        return {k: get_slices(slicers) for k, slicers in self.path_slicers.items()}
