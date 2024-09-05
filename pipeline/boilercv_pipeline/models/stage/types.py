"""Types."""

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from boilercv_pipeline.models.stage import DfsPlotsOuts

DfsPlotsOuts_T = TypeVar("DfsPlotsOuts_T", bound="DfsPlotsOuts", covariant=True)
