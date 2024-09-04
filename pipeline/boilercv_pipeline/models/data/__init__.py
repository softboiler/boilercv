"""Output data model."""

from typing import Generic

from pydantic import BaseModel, Field

from boilercv_pipeline.models.data import types as types  # noqa: PLC0414
from boilercv_pipeline.models.data.types import Dfs, Dfs_T, Plots, Plots_T


class Data(BaseModel, Generic[Dfs_T, Plots_T]):
    """Data frame and plot outputs."""

    dfs: Dfs_T = Field(default_factory=Dfs)
    plots: Plots_T = Field(default_factory=Plots)


AnyData = Data[Dfs, Plots]
