"""Types."""

from typing import TypeVar

from pandas import DataFrame
from pydantic import BaseModel


class NbOuts(BaseModel):
    """Notebook outputs."""


NbOuts_T = TypeVar("NbOuts_T", bound=NbOuts, covariant=True)
"""Notebook outs type."""


class DfNbOuts(NbOuts, arbitrary_types_allowed=True):
    """Notebook outputs with `df`."""

    df: DataFrame
