"""Subcooled bubble collapse experiment."""

from collections.abc import Iterable, Iterator
from concurrent.futures import Future, ProcessPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any, TypedDict

from boilercore.notebooks.namespaces import Params, get_nb_ns
from boilercore.paths import ISOLIKE, dt_fromisolike, get_module_name
from cmasher import get_sub_cmap
from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Colormap, Normalize
from matplotlib.pyplot import subplots
from numpy import any, histogram, sqrt, where
from pandas import CategoricalDtype, DataFrame, NamedAgg
from sparklines import sparklines

from boilercv.correlations.types import NbProcess
from boilercv.images import scale_bool
from boilercv.images.cv import Op, Transform, transform
from boilercv.types import DA, Img
from boilercv_pipeline.models.config import default

EXP = get_module_name(__spec__ or __file__)
"""Name of this experiment."""
DAY = "2024-07-18"
"""Day of the experiment"""
EXP_NBS = Path("docs/experiments") / EXP
"""Path to experiment notebooks."""
EXP_DATA = default.params.paths.experiments / EXP
"""Experimental data."""
ALL_THERMAL_DATA = EXP_DATA / f"{DAY}_all_thermal_data.csv"
"""All thermal data for this experiment."""
THERMAL_DATA = EXP_DATA / f"{DAY}_thermal.h5"
"""Reduced thermal data for this experiment."""
CENTERS = EXP_DATA / "centers"
"""Bubble centers."""
CONTOURS = EXP_DATA / "contours"
"""Bubble contours."""
OBJECTS = EXP_DATA / "objects"
"""Objects in each frame."""
TRACKPY_OBJECTS = EXP_DATA / "trackpy_objects"
"""Objects tracked by TrackPy."""
TRACKS = EXP_DATA / "tracks"
"""Object tracks."""
PROCESSED_TRACKS = EXP_DATA / "processed_tracks"
"""Processed object tracks."""
MERGED_TRACKS = EXP_DATA / "merged_tracks.h5"
"""Merged tracks."""
MAE = EXP_DATA / "mae"
"""Mean absolute error of tracks."""
MERGED_MAE = EXP_DATA / "merged_mae.h5"
"""Mean absolute error of tracks."""


def get_times(strings: Iterable[str]) -> Iterable[datetime]:
    """Get ISO-like timestamps."""
    for string in strings:
        if match := ISOLIKE.search(string):
            yield dt_fromisolike(match)


EXP_TIMES = list(get_times(path.stem for path in CONTOURS.iterdir()))


def save_df(path: Path, ns: SimpleNamespace):
    """Save a DataFrame to HDF5 format, handling invalid types."""
    name = path.stem
    getattr(ns, name).to_hdf(
        (path / f"{name}_{get_path_time(ns.p.time)}.h5"),
        key=path.stem,
        complib="zlib",
        complevel=9,
    )


def submit_nb_process(
    executor: ProcessPoolExecutor,
    nb: str,
    name: str,
    params: Params,
    process: NbProcess = save_df,
):
    """Submit a notebook process to an executor."""
    return executor.submit(
        apply_to_nb, nb=nb, name=name, params=params, process=process
    ).add_done_callback(check_result)


def check_result(future: Future[Any]):
    """Resolve a future, reporting an exception if there is one."""
    future.result()


def apply_to_nb(nb: str, name: str, params: Params, process: NbProcess = save_df):
    """Apply a process to a notebook."""
    (path := EXP_DATA / name).mkdir(exist_ok=True)
    process(path, get_nb_ns(nb=read_nb(nb), params=params))


def read_nb(nb: str) -> str:
    """Read a notebook for this experiment."""
    return (EXP_NBS / nb).with_suffix(".ipynb").read_text(encoding="utf-8")


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
