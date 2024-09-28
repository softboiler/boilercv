"""Types."""

from pathlib import Path
from typing import Annotated as Ann
from typing import TypeAlias, TypeVar

from pydantic import AfterValidator, BaseModel

from boilercv_pipeline.stages.binarize import Binarize
from boilercv_pipeline.stages.convert import Convert
from boilercv_pipeline.stages.fill import Fill
from boilercv_pipeline.stages.find_contours import FindContours
from boilercv_pipeline.stages.find_objects import FindObjects
from boilercv_pipeline.stages.find_tracks import FindTracks
from boilercv_pipeline.stages.get_thermal_data import GetThermalData
from boilercv_pipeline.stages.preview_binarized import PreviewBinarized
from boilercv_pipeline.stages.preview_filled import PreviewFilled
from boilercv_pipeline.stages.preview_gray import PreviewGray
from boilercv_pipeline.stages.skip_cloud import SkipCloud

Model_T = TypeVar("Model_T", bound=BaseModel)
"""Pydantic model type."""


def validate_relative(path: Path) -> Path:
    """Validate path is relative."""
    if path.is_absolute():
        raise ValueError(f"Path must be relative: {path}")
    return path


RelativePath: TypeAlias = Ann[Path, AfterValidator(validate_relative)]
"""Relative path."""

Stages: TypeAlias = (
    SkipCloud
    | Convert
    | Binarize
    | PreviewGray
    | PreviewBinarized
    | FindContours
    | Fill
    | PreviewFilled
    | GetThermalData
    | FindObjects
    | FindTracks
)
"""Model stages."""
