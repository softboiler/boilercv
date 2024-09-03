from pathlib import Path
from typing import Annotated, Self

from cappa.arg import Arg
from cappa.base import command
from pydantic import AfterValidator, Field, model_validator

from boilercv.data import FRAME
from boilercv_pipeline.models.deps import DirSlicer, get_slicers
from boilercv_pipeline.models.deps.types import Slicers
from boilercv_pipeline.models.path import DataDir, DirectoryPathSerPosix, DocsFile
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.paths.types import StagePaths
from boilercv_pipeline.stages.common.e230920 import Params, const


class Deps(StagePaths):
    stage: DirectoryPathSerPosix = Path(__file__).parent
    nb: DocsFile = paths.notebooks[stage.stem]
    contours: DataDir = paths.contours
    filled: DataDir = paths.filled


class Outs(StagePaths):
    dfs: DataDir = paths.e230920_objects
    plots: DataDir = paths.e230920_objects_plots


@command(
    invoke="boilercv_pipeline.stages.find_objects.__main__.main", default_long=True
)
class FindObjects(Params[Deps, Outs]):
    """Find objects."""

    deps: Annotated[Deps, Arg(hidden=True)] = Field(default_factory=Deps)
    """Stage dependencies."""
    outs: Annotated[Outs, Arg(hidden=True)] = Field(default_factory=Outs)
    """Stage outputs."""

    include_patterns: list[str] = const.include_patterns
    """Include patterns."""
    slicer_patterns: dict[str, Slicers] = Field(default_factory=dict)
    """Slicer patterns."""
    compare_with_trackpy: bool = False
    """Whether to get objects using the Trackpy approach."""
    guess_diameter: int = 21
    """Guess diameter for the Trackpy approach. (px)"""
    trackpy_cols: list[str] = ["y", "x", FRAME, "size"]
    """Columns to compare with the Trackpy approach."""
    cols: list[str] = [*trackpy_cols, "area", "diameter_px", "radius_of_gyration_px"]
    """Data to store."""

    contours: Annotated[
        list[Path],
        AfterValidator(
            lambda paths, info: paths
            or DirSlicer(
                path=info.data["deps"].contours,
                include_patterns=info.data["include_patterns"],
            ).paths
        ),
    ] = Field(default_factory=list)
    """Paths to filled video datasets to process."""
    filled: list[Path] = Field(default_factory=list)
    """Paths to filled video datasets to process."""
    filled_slicers: list[Slicers] = Field(default_factory=list)
    """Slicers for filled video datasets."""
    dfs: Annotated[
        list[Path],
        AfterValidator(
            lambda paths, info: paths
            or DirSlicer(
                path=info.data["outs"].dfs,
                include_patterns=info.data["include_patterns"],
            ).paths
        ),
    ] = Field(default_factory=list)
    """Paths to filled video datasets to process."""

    @model_validator(mode="after")
    def validate_filled(self) -> Self:
        """Validate attributes related to filled video datasets."""
        self.filled = (
            self.filled
            or DirSlicer(
                path=self.deps.filled, include_patterns=self.include_patterns
            ).paths
        )
        self.filled_slicers = [
            get_slicers(path, slicer_patterns=self.slicer_patterns)
            for path in self.filled
        ]
        return self
