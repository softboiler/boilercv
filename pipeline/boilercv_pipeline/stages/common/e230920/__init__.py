"""Subcooled bubble collapse experiment."""

from collections.abc import Iterator
from concurrent.futures import Future, ProcessPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from re import search
from typing import Any, TypedDict

from boilercore.notebooks.namespaces import get_nb_ns
from boilercore.paths import ISOLIKE, dt_fromisolike
from cmasher import get_sub_cmap
from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Colormap, Normalize
from matplotlib.pyplot import subplots
from numpy import any, histogram, sqrt, where
from pandas import CategoricalDtype, DataFrame, NamedAgg
from pydantic import BaseModel
from sparklines import sparklines

from boilercv.images import scale_bool
from boilercv.images.cv import Op, Transform, transform
from boilercv.types import DA, Img
from boilercv_pipeline.models.stages import AnyParams
from boilercv_pipeline.stages.common.e230920.types import DfNbOuts, Model


def get_times(directory: Path, pattern: str) -> list[str]:
    """Get timestamps from a pattern-filtered directory."""
    return [
        dt_fromisolike(match).isoformat()
        for path in directory.iterdir()
        if (match := ISOLIKE.search(path.stem)) and search(pattern, path.stem)
    ]


def get_time(path: Path) -> str:
    """Get timestamp from a path."""
    return match.group() if (match := ISOLIKE.search(path.stem)) else ""


def submit_nb_process(
    executor: ProcessPoolExecutor,
    nb: str,
    params: AnyParams,
    outs: type[Model] = DfNbOuts,
    **kwds: Any,
) -> Future[Model]:
    """Submit a notebook process to an executor."""
    return executor.submit(apply_to_nb, nb=nb, params=params, outs=outs, **kwds)


def apply_to_nb(
    nb: str, params: AnyParams, outs: type[Model] = DfNbOuts, **kwds: Any
) -> Model:
    """Apply a process to a notebook."""
    return outs.model_validate(
        get_nb_ns(nb=nb, params={"PARAMS": params.model_dump_json(), **kwds}).outs
    )


def save_df(future: Future[DfNbOuts], dfs: Path, dep: Path):
    """Save a DataFrame to HDF5 format."""
    future.result().df.to_hdf(
        dfs / f"{dfs.stem}_{time}.h5" if (time := get_time(dep)) else f"{dfs.stem}.h5",
        key=dfs.stem,
        complib="zlib",
        complevel=9,
    )


def get_path_time(time: str) -> str:
    """Get a path-friendly time string."""
    return time.replace(":", "-")


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


def plot_composite_da(video: DA, ax: Axes | None = None) -> Axes:
    """Compose a video-like data array and highlight the first frame."""
    first_frame = video.sel(frame=0).values
    composite_video = video.max("frame").values
    with bounded_ax(composite_video, ax) as ax:
        ax.imshow(~first_frame, alpha=0.6)
        ax.imshow(~composite_video, alpha=0.2)
    return ax


@contextmanager
def bounded_ax(img: Img, ax: Axes | None = None) -> Iterator[Axes]:
    """Show only the region bounding nonzero elements of the image."""
    ylim, xlim = get_image_boundaries(img)
    if ax:
        bound_ax = ax
    else:
        _, bound_ax = subplots()
    bound_ax.set_xlim(*xlim)  # pyright: ignore[reportAttributeAccessIssue], CI
    bound_ax.set_ylim(*ylim)  # pyright: ignore[reportAttributeAccessIssue], CI
    bound_ax.invert_yaxis()
    yield bound_ax  # pyright: ignore[reportReturnType], CI


def get_image_boundaries(img) -> tuple[tuple[int, int], tuple[int, int]]:
    """Get the boundaries of an image."""
    dilated = transform(scale_bool(img), Transform(Op.dilate, 12))
    cols = any(dilated, axis=0)
    rows = any(dilated, axis=1)
    ylim = tuple(where(rows)[0][[0, -1]])
    xlim = tuple(where(cols)[0][[0, -1]])
    return ylim, xlim


def crop_image(img, ylim, xlim):
    """Crop an image to the specified boundaries."""
    return img[ylim[0] : ylim[1] + 1, xlim[0] : xlim[1] + 1]


WIDTH = 10


def get_hists(df: DataFrame, groupby: str, cols: list[str]) -> DataFrame:
    """Add sparklines row to the top of a dataframe."""
    df = df.groupby(groupby, **GBC).agg(**{  # pyright: ignore[reportArgumentType, reportCallIssue]
        col: NamedAgg(column=col, aggfunc=sparkhist) for col in cols
    })
    # Can't one-shot this because of the comprehension {...: ... for col in hist_cols}
    return df.assign(**{col: df[col].str.center(WIDTH, "▁") for col in cols})


def sparkhist(grp: DataFrame) -> str:
    """Render a sparkline histogram."""
    num_lines = 1  # Sparklines don't render properly across multiple lines
    bins = min(WIDTH - 2, int(sqrt(grp.count())))
    histogram_, _edges = histogram(grp, bins=bins)
    return "\n".join(sparklines(histogram_, num_lines))


@dataclass
class Col:
    """Column transformation."""

    old: str
    new: str = ""
    old_unit: str = ""
    new_unit: str = ""
    scale: float = 1

    def __post_init__(self):
        self.new = self.new or self.old
        self.new_unit = self.new_unit or self.old_unit
        self.new = f"{self.new} ({self.new_unit})" if self.new_unit else self.new


class Columns(BaseModel, use_attribute_docstrings=True):
    """Columns."""

    frame: Col = Col("frame", "Frame #")


def transform_cols(df: DataFrame, cols: list[Col], drop: bool = True) -> DataFrame:
    """Transform dataframe columns."""
    df = df.assign(**{
        col.new: df[col.old] if col.scale == 1 else df[col.old] * col.scale
        for col in cols
    })
    return df[[col.new for col in cols]] if drop else df


class Conversion(TypedDict):
    """Scalar conversion between units."""

    old_unit: str
    new_unit: str
    scale: float


M_TO_MM = Conversion(old_unit="m", new_unit="mm", scale=1000)


def get_cat_colorbar(
    ax: Axes, col: str, palette: Any, data: DataFrame, alpha: float = 1.0
) -> tuple[list[tuple[float, float, float]], DataFrame]:
    """Get categorical colorbar."""
    if isinstance(data[col].dtype, CategoricalDtype):
        data[col] = data[col].cat.remove_unused_categories()
        num_colors = len(data[col].cat.categories)
    else:
        num_colors = data[col].nunique()
    palette = get_first_from_palette(palette, num_colors)
    mappable = ScalarMappable(cmap=palette, norm=Normalize(0, num_colors))
    mappable.set_array([])
    colorbar = ax.figure.colorbar(ax=ax, mappable=mappable, label=col, alpha=alpha)  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess], CI
    colorbar.set_ticks([])
    return palette.colors, data


def get_first_from_palette(palette: Any, n: int) -> Colormap:
    """Get the first `n` colors from a palette."""
    return get_sub_cmap(
        palette, start=0, stop=n / (getattr(palette, "N", None) or len(palette)), N=n
    )
