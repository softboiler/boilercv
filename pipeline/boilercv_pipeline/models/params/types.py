"""Types."""

from typing import ParamSpec, Protocol, TypeVar

from pandas import DataFrame

from boilercv_pipeline.models.data import Data
from boilercv_pipeline.models.data.types import Dfs, Plots
from boilercv_pipeline.models.stage import StagePaths

Deps_T = TypeVar("Deps_T", bound=StagePaths, covariant=True)
"""Dependencies type."""
Outs_T = TypeVar("Outs_T", bound=StagePaths, covariant=True)
"""Outputs type."""
Data_T = TypeVar("Data_T", bound=Data[Dfs, Plots], covariant=True)
"""Model type."""

Ps = ParamSpec("Ps")
"""Parameter type specification."""


class Preview(Protocol[Ps]):  # noqa: D101
    def __call__(  # noqa: D102
        self, df: DataFrame, /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> DataFrame: ...
