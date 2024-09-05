"""Types."""

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from boilercv_pipeline.models.subcool import FilledDeps

FilledDeps_T = TypeVar("FilledDeps_T", bound="FilledDeps")
