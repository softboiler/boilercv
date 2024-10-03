"""Subcooling study-specific models."""

from functools import partial
from pathlib import Path
from typing import Annotated as Ann
from typing import Generic

from cappa.arg import Arg
from context_models.validators import ContextAfterValidator
from pydantic import AfterValidator, BaseModel, Field, ValidationInfo

from boilercv.data import FRAME
from boilercv_pipeline.models.deps import DirSlicer, first_slicer, get_slicers
from boilercv_pipeline.models.deps.types import Slicers
from boilercv_pipeline.models.params import DataParams
from boilercv_pipeline.models.params.types import Data_T, Deps_T, Outs_T
from boilercv_pipeline.models.path import (
    DataDir,
    DirectoryPathSerPosix,
    DocsFile,
    get_time,
)
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.stage import DataStage, Deps
from boilercv_pipeline.models.stage.types import DfsPlotsOuts_T
from boilercv_pipeline.models.subcool.types import FilledDeps_T
from boilercv_pipeline.parser import PairedArg
from boilercv_pipeline.sync_dvc.validators import (
    dvc_extend_with_timestamp_suffixed_plots,
    dvc_set_only_sample,
)


class Constants(BaseModel):
    """Subcool study constants."""

    day: str = "2024-07-18"
    """Default sample day."""
    time: str = "17-44-35"
    """Default sample time."""
    nb_frame_count: int = 500
    """Default frame count in notebooks."""
    nb_frame_step: int = 1
    """Default step between frames in notebooks."""
    data_stage: DataStage = DataStage()
    """Common stages of data processing."""

    @property
    def nb_slicer_patterns(self) -> dict[str, Slicers]:
        """Slicer patterns for notebook runs."""
        return {
            r".+": {FRAME: first_slicer(n=self.nb_frame_count, step=self.nb_frame_step)}
        }

    @property
    def sample(self) -> str:
        """Sample to process."""
        return f"{self.day}T{self.time}"

    @property
    def nb_include_patterns(self) -> list[str]:
        """Include patterns for a single sample."""
        return [rf"^.*{self.sample}.*$"]

    @property
    def include_patterns(self) -> list[str]:
        """Include patterns."""
        return [rf"^.*{self.day}.*$"]


const = Constants()


def validate_time_suffixed_paths(
    paths: list[Path],
    info: ValidationInfo,
    times_field: str,
    paths_field: str,
    paths_subfield: str,
    prefix: str = "",
    subfield_prefix: bool = True,
    ext: str = "h5",
) -> list[Path]:
    """Validate time-suffixed paths."""
    return paths or [
        (
            Path(getattr(info.data[paths_field], paths_subfield))
            / (
                f"{prefix or paths_subfield}_{time}.{ext}"
                if subfield_prefix
                else Path(f"{time}.{ext}")
            )
        )
        for time in info.data[times_field]
    ]


class SubcoolParams(
    DataParams[Deps_T, Outs_T, Data_T], Generic[Deps_T, Outs_T, Data_T]
):
    """Stage parameters for the subcooled boiling study."""

    sample: str = const.sample
    """Sample to process."""
    only_sample: Ann[
        bool,
        PairedArg("only_sample"),
        ContextAfterValidator(partial(dvc_set_only_sample, sample_field="sample")),
    ] = False
    """Only process the sample."""
    include_patterns: Ann[
        list[str],
        AfterValidator(
            lambda include_patterns, info: (
                [rf"^.*{info.data['sample']}.*$"]
                if info.data["only_sample"]
                else include_patterns
            )
        ),
    ] = const.include_patterns
    """Include patterns."""


class FilledDeps(Deps):
    """Dependencies for subcooled boiling study including filled video dataset."""

    stage: DirectoryPathSerPosix
    nb: DocsFile
    filled: DataDir = paths.filled


class FilledParams(
    SubcoolParams[FilledDeps_T, DfsPlotsOuts_T, Data_T],
    Generic[FilledDeps_T, DfsPlotsOuts_T, Data_T],
):
    """Stage parameters for subcooled boiling study including filled video dataset."""

    frame_count: int = 0
    """Count of frames."""
    frame_step: int = 1
    """Step between frames."""
    slicer_patterns: dict[str, Slicers] = Field(default_factory=dict)
    """Slicer patterns."""
    filled: Ann[
        list[Path],
        Arg(hidden=True),
        AfterValidator(
            lambda paths, info: (
                paths
                or DirSlicer(
                    path=info.data["deps"].filled,
                    include_patterns=info.data["include_patterns"],
                ).paths
            )
        ),
    ] = Field(default_factory=list)
    """Paths to filled video datasets."""
    filled_slicers: Ann[
        list[Slicers],
        Arg(hidden=True),
        AfterValidator(
            lambda slicers, info: slicers
            or [
                get_slicers(
                    path,
                    slicer_patterns=(
                        info.data["slicer_patterns"]
                        or {
                            r".+": {
                                FRAME: first_slicer(
                                    n=info.data["frame_count"],
                                    step=info.data["frame_step"],
                                )
                            }
                        }
                    ),
                )
                for path in info.data["filled"]
            ]
        ),
    ] = Field(default_factory=list)
    """Slicers for filled video datasets."""
    times: Ann[
        list[str],
        Arg(hidden=True),
        AfterValidator(
            lambda times, info: times
            or [get_time(path) for path in info.data["filled"]]
        ),
        ContextAfterValidator(dvc_extend_with_timestamp_suffixed_plots),
    ] = Field(default_factory=list)
    dfs: list[Path]
    """Paths to data frame stage outputs."""
