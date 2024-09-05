"""Subcooling study-specific models."""

from typing import Generic

from pydantic import BaseModel

from boilercv.data import FRAME
from boilercv_pipeline.models import params
from boilercv_pipeline.models.deps import first_slicer
from boilercv_pipeline.models.deps.types import Slicers
from boilercv_pipeline.models.params.types import Data_T, Deps_T, Outs_T


class Constants(BaseModel):
    """Subcool study constants."""

    day: str = "2024-07-18"
    time: str = "17-44-35"
    nb_slicer_patterns: dict[str, Slicers] = {
        r".+": {FRAME: first_slicer(n=10, step=100)}
    }
    """Slicer patterns representing a small subset of frames."""

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


class SubcoolParams(
    params.DataParams[Deps_T, Outs_T, Data_T], Generic[Deps_T, Outs_T, Data_T]
):
    """Stage parameters for `e230920`."""

    sample: str = const.sample
    """Sample to process."""
    include_patterns: list[str] = const.include_patterns
    """Include patterns."""
