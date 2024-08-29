"""Types."""

from typing import TypeVar

from pandas import DataFrame
from pydantic import BaseModel

Model = TypeVar("Model", bound=BaseModel, covariant=True)
"""Model type."""
Nb_T = TypeVar("Nb_T", bound=BaseModel, covariant=True)
"""Notebook model type."""


class NbOuts(BaseModel):
    """Notebook outputs."""


class DfNbOuts(NbOuts, arbitrary_types_allowed=True):
    """Notebook outputs with `df`."""

    df: DataFrame
