"""Types."""

from typing import TypeVar

from matplotlib.figure import Figure
from pandas import DataFrame
from pydantic import BaseModel, Field

Model = TypeVar("Model", bound=BaseModel, covariant=True)
"""Model type."""


class NbOuts(BaseModel):
    """Notebook outputs."""


class DfNbOuts(NbOuts, arbitrary_types_allowed=True):
    """Notebook outputs with data frames and plots."""

    df: DataFrame = Field(default_factory=DataFrame)
    plots: list[Figure] = Field(default_factory=list)
