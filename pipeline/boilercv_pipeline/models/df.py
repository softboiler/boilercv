"""Data frame model."""

from typing import TypedDict

from pandas import DataFrame, NamedAgg
from pandas.api.typing import DataFrameGroupBy  # pyright: ignore[reportMissingImports]


class GroupByCommon(TypedDict):
    """Common groupby parameters."""

    as_index: bool
    dropna: bool
    observed: bool
    group_keys: bool
    sort: bool


GBC = GroupByCommon(
    as_index=False, dropna=False, observed=True, group_keys=False, sort=False
)


def gbc(
    as_index: bool = False,
    dropna: bool = False,
    observed: bool = True,
    group_keys: bool = False,
    sort: bool = False,
):
    """Get common groupby parameters."""
    return GBC | GroupByCommon(**locals())


WIDTH = 10


def agg(dfgb: DataFrameGroupBy, cols: dict[str, NamedAgg]) -> DataFrame:
    """Pandas group aggregator for correct types."""
    return dfgb.agg(**cols)
