"""Types."""

from typing import TypeVar

from pandas import DataFrame
from pydantic import BaseModel, Field


class Dfs(BaseModel, arbitrary_types_allowed=True):
    """Data frames."""

    src: DataFrame = Field(default_factory=DataFrame)
    dst: DataFrame = Field(default_factory=DataFrame)


Dfs_T = TypeVar("Dfs_T", bound=Dfs, covariant=True)


class Plots(BaseModel, arbitrary_types_allowed=True):
    """Plots."""


Plots_T = TypeVar("Plots_T", bound=Plots, covariant=True)
