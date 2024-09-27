"""Data frame operations."""

from pathlib import Path

from numpy import histogram, sqrt
from pandas import DataFrame, NamedAgg
from sparklines import sparklines

from boilercv_pipeline.models.df import GBC, WIDTH


def sparkhist(grp: DataFrame) -> str:
    """Render a sparkline histogram."""
    num_lines = 1  # Sparklines don't render properly across multiple lines
    bins = min(WIDTH - 2, int(sqrt(grp.count())))
    histogram_, _edges = histogram(grp, bins=bins)
    return "\n".join(sparklines(histogram_, num_lines))


def get_hists(df: DataFrame, groupby: str, cols: list[str]) -> DataFrame:
    """Add sparklines row to the top of a dataframe."""
    df = df.groupby(groupby, **GBC).agg(**{  # pyright: ignore[reportArgumentType, reportCallIssue]
        col: NamedAgg(column=col, aggfunc=sparkhist) for col in cols
    })
    # Can't one-shot this because of the comprehension {...: ... for col in hist_cols}
    return df.assign(**{col: df[col].str.center(WIDTH, "▁") for col in cols})


def save_df(df: DataFrame, path: Path | str, key: str | None = None):
    """Save data frame to a compressed HDF5 file."""
    path = Path(path)
    df.to_hdf(path, key=key or path.stem, complib="zlib", complevel=9)


def save_dfs(dfs: dict[str, DataFrame], path: Path | str, key: str | None = None):
    """Save data frame to a compressed HDF5 file."""
    path = Path(path)
    for key, df in dfs.items():
        save_df(df, path, key=key)


def limit_group_size(df: DataFrame, by: str | list[str], n: int) -> DataFrame:
    """Filter out groups shorter than a certain length."""
    count = "__count"  # ? Dunder triggers forbidden control characters
    return (
        df.assign(**{
            count: lambda df: df.groupby(by, **GBC)[
                [by[0] if isinstance(by, list) else by]
            ].transform("count")
        })
        .query(f"`{count}` > {n}")
        .drop(columns=count)
    )
