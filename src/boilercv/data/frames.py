"""Dataframes."""

from numpy import split
from pandas import DataFrame, concat

from boilercv.data import YX_PX
from boilercv.types import DF, ArrayLike


def df_points(points: ArrayLike, dims: list[str] = YX_PX) -> DF:
    """Build a dataframe from an array of points."""
    return (
        DataFrame(
            columns=dims,
            data=points,  # type: ignore  # pyright 1.1.333
        )
        .rename_axis(axis="index", mapper="point")
        .rename_axis(axis="columns", mapper="dim")
    )


def frame_lines(lines: ArrayLike) -> DF:
    """Build a dataframe from an array of line segments."""
    ordered_pairs = [df_points(point) for point in split(lines, 2, axis=1)]
    return (
        concat(axis="columns", keys=[0, 1], objs=ordered_pairs)
        .rename_axis(axis="index", mapper="line")
        .rename_axis(axis="columns", mapper=["coord", "dim"])
        .reorder_levels(axis="columns", order=["dim", "coord"])
    )
