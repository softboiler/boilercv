from pathlib import Path
from typing import Annotated

from cappa.arg import Arg
from cappa.base import command
from pydantic import BaseModel, Field

from boilercv.data import FRAME
from boilercv_pipeline.models.deps import DirSlicer, first_slicer
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.paths.types import StagePaths
from boilercv_pipeline.models.types import Slicer, Slicers
from boilercv_pipeline.models.types.runtime import (
    DataDir,
    DirectoryPathSerPosix,
    DocsFile,
)
from boilercv_pipeline.stages.common.e230920 import Params, const

SLICER_PATTERNS = {r".+": {FRAME: first_slicer(n=10, step=100)}}
"""Slicer patterns."""


class Deps(StagePaths):
    stage: DirectoryPathSerPosix = Path(__file__).parent
    nb: DocsFile = paths.notebooks[stage.stem]
    contours: DataDir = paths.contours
    filled: DataDir = paths.filled


class Outs(StagePaths):
    dfs: DataDir = paths.e230920_objects
    plots: DataDir = paths.e230920_objects_plots


class Nb(BaseModel):
    contours: Path = Path()
    filled: Path = Path()
    filled_slicers: dict[str, Slicer] = Field(default_factory=dict)


@command(
    invoke="boilercv_pipeline.stages.find_objects.__main__.main", default_long=True
)
class FindObjects(Params[Deps, Outs, Nb]):
    """Find objects."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    """Stage dependencies."""
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
    """Stage outputs."""
    nb: Nb = Field(default_factory=Nb)
    """Notebook-only params."""
    slicer_patterns: dict[str, Slicers] = SLICER_PATTERNS
    """Slicer patterns."""
    compare_with_trackpy: bool = True
    """Whether to get objects using the Trackpy approach."""
    guess_diameter: int = 21
    """Guess diameter for the Trackpy approach. (px)"""
    trackpy_cols: list[str] = ["y", "x", FRAME, "size"]
    """Columns to compare with the Trackpy approach."""
    cols: list[str] = [*trackpy_cols, "area", "diameter_px", "radius_of_gyration_px"]
    """Data to store."""


def get_nb(deps: Deps) -> Nb:
    all_contours = DirSlicer(
        path=deps.contours, include_patterns=const.single_sample_include_pattern
    )
    all_filled = DirSlicer(
        path=deps.filled,
        include_patterns=const.single_sample_include_pattern,
        slicer_patterns=SLICER_PATTERNS,
    )
    for contours, filled in zip(all_contours.paths, all_filled.paths, strict=True):
        return Nb(
            contours=contours,
            filled=filled,
            filled_slicers=all_filled.path_slicers[filled],
        )
    return Nb()
