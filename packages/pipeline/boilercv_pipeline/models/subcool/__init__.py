"""Subcooling study-specific models."""

from functools import partial
from pathlib import Path
from typing import Annotated as Ann
from typing import Generic, Self

from cappa.arg import Arg
from context_models import CONTEXT
from context_models.validators import ContextAfterValidator, context_model_validator
from pydantic import AfterValidator, BaseModel, Field, ValidationInfo

from boilercv.data import FRAME
from boilercv_pipeline.models.contexts import DVC
from boilercv_pipeline.models.contexts.types import BoilercvPipelineValidationInfo
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


class Constants(BaseModel):
    """Subcool study constants."""

    day: str = "2024-07-18"
    time: str = "17-44-35"

    nb_frame_count: int = 500
    nb_frame_step: int = 1

    @property
    def nb_slicer_patterns(self) -> dict[str, Slicers]:
        """Slicer patterns for notebook runs."""
        return {
            r".+": {FRAME: first_slicer(n=self.nb_frame_count, step=self.nb_frame_step)}
        }

    data_stage: DataStage = DataStage()
    """Common stages of data processing."""

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


def validate_paths(
    paths: list[Path] | None, info: ValidationInfo, deps: bool, field: str
) -> list[Path]:
    """Get paths for a given paths field in dependencies."""
    return (
        paths
        or DirSlicer(
            path=getattr(info.data["deps" if deps else "outs"], field),
            include_patterns=info.data["include_patterns"],
        ).paths
    )


def get_include_patterns(
    include_patterns: list[str], info: ValidationInfo
) -> list[str]:
    """Get include patterns."""
    if info.data["only_sample"]:
        return [rf"^.*{info.data['sample']}.*$"]
    return include_patterns


class SubcoolParams(
    DataParams[Deps_T, Outs_T, Data_T], Generic[Deps_T, Outs_T, Data_T]
):
    """Stage parameters for the subcooled boiling study."""

    sample: str = const.sample
    """Sample to process."""
    only_sample: Ann[bool, PairedArg("only_sample")] = False
    """Only process the sample."""
    include_patterns: Ann[list[str], AfterValidator(get_include_patterns)] = (
        const.include_patterns
    )
    """Include patterns."""


class FilledDeps(Deps):
    """Dependencies for subcooled boiling study including filled video dataset."""

    stage: DirectoryPathSerPosix
    nb: DocsFile
    filled: DataDir = paths.filled


def validate_times(times: list[str], info: ValidationInfo, field: str) -> list[str]:
    """Validate times."""
    return times or [get_time(path) for path in info.data.get(field, [])]


def validate_slicers(
    slicers: list[Slicers] | None, info: ValidationInfo, field: str
) -> list[Slicers]:
    """Get slicers for a given paths field in parameters."""
    return slicers or [
        get_slicers(
            path,
            slicer_patterns=(
                info.data["slicer_patterns"]
                or {
                    r".+": {
                        FRAME: first_slicer(
                            n=info.data["frame_count"], step=info.data["frame_step"]
                        )
                    }
                }
            ),
        )
        for path in info.data.get(field, [])
    ]


def dvc_validate_times(
    times: list[str], info: BoilercvPipelineValidationInfo
) -> list[str]:
    """Validate plot timestamp suffixes for `dvc.yaml`."""
    if info.field_name != CONTEXT and (dvc := info.context.get(DVC)) and dvc.plot_dir:
        dvc.stage.plots.extend(
            sorted(
                (dvc.plot_dir / ("_".join([f"{name}", time]) + ".png")).as_posix()
                for name in dvc.plot_names
                for time in times
            )
        )
        dvc.plot_dir = None
        dvc.plot_names.clear()
    return times


class FilledParams(
    SubcoolParams[FilledDeps_T, DfsPlotsOuts_T, Data_T],
    Generic[FilledDeps_T, DfsPlotsOuts_T, Data_T],
):
    """Stage parameters for subcooled boiling study including filled video dataset."""

    @context_model_validator(mode="after")
    def dvc_validate_params(self, info: BoilercvPipelineValidationInfo) -> Self:
        """Extend stage plots in `dvc.yaml`."""
        if (
            info.field_name != CONTEXT
            and (dvc := info.context.get(DVC))
            and dvc.plot_dir
            and not dvc.stage.plots
        ):
            dvc.stage.plots.extend(
                sorted(
                    (dvc.plot_dir / f"{name}.png").as_posix() for name in dvc.plot_names
                )
            )
            dvc.plot_dir = None
            dvc.plot_names.clear()
        return self

    frame_count: int = 0
    """Count of frames."""
    frame_step: int = 1
    """Step between frames."""
    dfs: Ann[
        list[Path],
        Arg(hidden=True),
        AfterValidator(partial(validate_paths, deps=False, field="dfs")),
    ] = Field(default_factory=list)
    """Paths to data frame stage outputs."""
    slicer_patterns: dict[str, Slicers] = Field(default_factory=dict)
    """Slicer patterns."""
    filled: Ann[
        list[Path],
        Arg(hidden=True),
        AfterValidator(partial(validate_paths, deps=True, field="filled")),
    ] = Field(default_factory=list)
    """Paths to filled video datasets."""
    filled_slicers: Ann[
        list[Slicers],
        Arg(hidden=True),
        AfterValidator(partial(validate_slicers, field="filled")),
    ] = Field(default_factory=list)
    """Slicers for filled video datasets."""
    times: Ann[
        list[str],
        Arg(hidden=True),
        AfterValidator(partial(validate_times, field="filled")),
        ContextAfterValidator(dvc_validate_times),
    ] = Field(default_factory=list)
