"""Types."""

from typing import TYPE_CHECKING, Any, ParamSpec, Protocol, TypeAlias, TypeVar

from pandas import DataFrame, Series

from boilercv_pipeline.models.data import Data, Dfs, Plots
from boilercv_pipeline.models.stage import Deps, Outs

if TYPE_CHECKING:
    from boilercv_pipeline.models.params import Params

DfOrS_T = TypeVar("DfOrS_T", bound="DataFrame | Series[Any]")
"""DataFrame or Series type."""
Deps_T = TypeVar("Deps_T", bound=Deps, covariant=True)
"""Dependencies type."""
Outs_T = TypeVar("Outs_T", bound=Outs, covariant=True)
"""Outputs type."""
Data_T = TypeVar("Data_T", bound=Data[Dfs, Plots], covariant=True)
"""Model type."""
Ps = ParamSpec("Ps")
"""Parameter type specification."""
AnyParams: TypeAlias = "Params[Deps, Outs]"
"""Any parameters."""


class Preview(Protocol[Ps]):  # noqa: D101
    def __call__(  # noqa: D102
        self, df: DataFrame, /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> DataFrame: ...
