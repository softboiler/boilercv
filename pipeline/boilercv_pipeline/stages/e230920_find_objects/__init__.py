from pathlib import Path

from cappa.base import command, invoke
from pydantic import BaseModel, DirectoryPath, Field

from boilercv.data import FRAME
from boilercv_pipeline.models.deps import DirSlicer, Slicer, Slicers, first_slicer
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.stages import Params, StagePaths
from boilercv_pipeline.models.types.runtime import DataDir, DocsFile


class Deps(StagePaths):
    stage: DirectoryPath = Path(__file__).parent
    nb: DocsFile = paths.notebooks[stage.stem]
    contours: DataDir = paths.contours
    filled: DataDir = paths.filled


class Outs(StagePaths):
    dfs: DataDir = paths.e230920_objects


class Nb(BaseModel):
    contours: Path = Path()
    filled: Path = Path()
    filled_slicers: dict[str, Slicer] = Field(default_factory=dict)


def get_nb(deps: Deps, stem: str = "2024-07-18T17-44-35") -> Nb:
    include_patterns: list[str] = [r"^2024-07-18.+$"]
    all_contours = DirSlicer(path=deps.contours, include_patterns=include_patterns)
    all_filled = DirSlicer(
        path=deps.filled,
        include_patterns=include_patterns,
        slicer_patterns={r".+": {FRAME: first_slicer(n=3, step=10)}},
    )
    for contours, filled in zip(all_contours.paths, all_filled.paths, strict=True):
        if contours.stem == stem:
            return Nb(
                contours=contours,
                filled=filled,
                filled_slicers=all_filled.path_slicers[filled],
            )
    return Nb()


@command(
    invoke="boilercv_pipeline.stages.e230920_find_objects.__main__.main",
    default_long=True,
)
class E230920FindObjects(Params[Deps, Outs]):
    """Find objects."""

    deps: Deps = Field(default_factory=Deps)
    outs: Outs = Field(default_factory=Outs)
    compare_with_trackpy: bool = False
    """Whether to get objects using the Trackpy approach."""
    guess_diameter: int = 21
    """Guess diameter for the Trackpy approach. (px)"""
    trackpy_cols: list[str] = ["y", "x", FRAME, "size"]
    """Columns to compare with the Trackpy approach."""
    cols: list[str] = [*trackpy_cols, "area", "diameter_px", "radius_of_gyration_px"]
    """Data to store."""
    sample: str = "2024-07-18T17-44-35"
    """Sample to process."""
    include_patterns: list[str] = [r"^2024-07-18.+$"]
    """Include patterns."""
    slicer_patterns: dict[str, Slicers] = {r".+": {FRAME: first_slicer(n=3, step=10)}}
    """Slicer patterns."""
    nb: Nb = Field(default_factory=Nb)
    """Notebook-only params."""


if __name__ == "__main__":
    invoke(E230920FindObjects)
