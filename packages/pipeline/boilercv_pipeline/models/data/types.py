"""Types."""

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from boilercv_pipeline.models.data import Dfs, Plots

Dfs_T = TypeVar("Dfs_T", bound="Dfs", covariant=True)
Plots_T = TypeVar("Plots_T", bound="Plots", covariant=True)
