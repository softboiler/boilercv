"""Output data model."""

from typing import Generic

from pandas import DataFrame
from pydantic import BaseModel, Field

from boilercv_pipeline.models.data.types import Dfs_T, Plots_T


class Dfs(BaseModel, arbitrary_types_allowed=True):
    """Data frames."""

    src: DataFrame = Field(default_factory=DataFrame)
    dst: DataFrame = Field(default_factory=DataFrame)


class Plots(BaseModel, arbitrary_types_allowed=True):
    """Plots."""


class Data(BaseModel, Generic[Dfs_T, Plots_T]):
    """Data frame and plot outputs."""

    dfs: Dfs_T = Field(default_factory=Dfs)
    plots: Plots_T = Field(default_factory=Plots)


AnyData = Data[Dfs, Plots]
