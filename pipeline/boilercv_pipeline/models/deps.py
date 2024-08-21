"""Dependency models."""

from functools import cached_property
from pathlib import Path
from re import Pattern, compile
from typing import Generic, TypeAlias, TypeVar

from pydantic import Field

from boilercv_pipeline.models.stages import StagePaths

Slicer: TypeAlias = tuple[int | None, ...]
DfSlicer: TypeAlias = Slicer
DaSlicer: TypeAlias = dict[str, Slicer]
Slicer_T = TypeVar("Slicer_T", bound=DfSlicer | DaSlicer, covariant=True)


def first_slicer(n: int | None, step: int = 1) -> Slicer:
    """Slicer for the first `n` elements taken at `step`s."""
    return (None, *[step * f for f in (n - 1, 1)]) if n else (None, None, step)


class DepDir(StagePaths, Generic[Slicer_T]):
    """Dependency directory."""

    path: Path
    include: list[str] = Field(default_factory=list)
    exclude: list[str] = Field(default_factory=list)
    include_patterns: list[str] = Field(default_factory=list)
    exclude_patterns: list[str] = Field(default_factory=list)
    slicers: dict[str, Slicer_T] = Field(default_factory=dict)
    slicer_patterns: dict[str, Slicer_T] = Field(default_factory=dict)

    @cached_property
    def include_patterns_(self) -> list[Pattern[str]]:
        """Compiled include patterns."""
        return [compile(pat) for pat in self.include_patterns]

    @cached_property
    def exclude_patterns_(self) -> list[Pattern[str]]:
        """Compiled exclude patterns."""
        return [compile(pat) for pat in self.exclude_patterns]

    @cached_property
    def slice_patterns_(self) -> dict[Pattern[str], Slicer_T]:
        """Compiled exclude patterns."""
        return {compile(pat): slice_ for pat, slice_ in self.slicer_patterns.items()}


class Dep(StagePaths, Generic[Slicer_T]):
    """Path to a dependency."""

    path: Path
    slicer: Slicer_T


class DaDep(Dep[DaSlicer]):
    """Path to a dependency."""

    @property
    def slices(self) -> dict[str, slice]:
        """Slices."""
        return {k: slice(*v) for k, v in self.slicer.items()}


class DfDep(Dep[DfSlicer]):
    """Path to a dependency."""

    @property
    def slice(self) -> slice:
        """Slice."""
        return slice(*self.slicer)


class DfDepDir(DepDir[DfSlicer]):
    """Dependency directory."""

    @property
    def paths(self) -> list[DfDep]:
        """Filtered paths."""
        return filter_paths(self, DfDep)


class DaDepDir(DepDir[DaSlicer]):
    """Dependency directory."""

    @property
    def paths(self) -> list[DaDep]:
        """Filtered paths."""
        return filter_paths(self, DaDep)


Dep_T = TypeVar("Dep_T", bound=DaDep | DfDep)


def filter_paths(
    dep_dir: DepDir[DfSlicer | DaSlicer], dep_typ: type[Dep_T]
) -> list[Dep_T]:
    """Filter paths."""
    paths = []
    for file in dep_dir.path.iterdir():
        if (
            (dep_dir.include and file.stem not in dep_dir.include)  # noqa: PLR0916
            or file.stem in dep_dir.exclude
            or (
                dep_dir.include_patterns
                and not any(pat.search(file.stem) for pat in dep_dir.include_patterns_)
            )
            or any(pat.search(file.stem) for pat in dep_dir.exclude_patterns_)
        ):
            continue
        slicer: DfSlicer | DaSlicer = (None,) if issubclass(dep_typ, DfDep) else {}
        if dep_dir.slicers:
            slicer = dep_dir.slicers.get(file.stem, slicer)
        if dep_dir.slicer_patterns:
            for pat, slicer_ in dep_dir.slice_patterns_.items():
                if pat.search(file.stem):
                    slicer = slicer_
                    break
        paths.append(dep_typ(_context=dep_dir._context, path=file, slicer=slicer))  # noqa: SLF001  # pyright: ignore[reportArgumentType]
    return paths
