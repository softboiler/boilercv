"""Subcooled bubble collapse experiment."""

from collections.abc import Callable, Iterable, Iterator
from concurrent.futures import Future, ProcessPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from re import search
from typing import Annotated, Any, Generic, Self, TypedDict

import numpy
from boilercore.notebooks.namespaces import get_nb_ns
from boilercore.paths import ISOLIKE, dt_fromisolike
from cmasher import get_sub_cmap
from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Colormap, Normalize
from matplotlib.figure import Figure
from matplotlib.pyplot import subplots
from numpy import histogram, sqrt, where
from pandas import CategoricalDtype, DataFrame, NamedAgg
from pydantic import BaseModel, model_validator
from sparklines import sparklines

from boilercv.data import FRAME, PX, X, Y
from boilercv.images import scale_bool
from boilercv.images.cv import Op, Transform, transform
from boilercv.types import DA, Img
from boilercv_pipeline.models import stages
from boilercv_pipeline.models.deps import first_slicer
from boilercv_pipeline.models.deps.types import Slicers
from boilercv_pipeline.models.paths.types import Deps_T, Outs_T
from boilercv_pipeline.models.stages import AnyParams
from boilercv_pipeline.stages.common.e230920.types import DfNbOuts, Model

IDX = "idx"
SRC = "src"
DST = "dst"


def get_unit(unit: str) -> str:
    """Get unit label."""
    return f"°{unit}" if unit == "C" else unit


def get_parts(label: str) -> tuple[str, str, str]:
    """Get parts of a label."""
    if m := search(
        r"^(?P<sym>[^_\()]+)(?P<sub>_[^\s]+)?\s?\(?(?P<unit>[^)]+)?\)?$", label
    ):
        return (
            m["sym"].strip(),
            (m["sub"] or "").removeprefix("_").strip(),
            (m["unit"] or "").strip(),
        )
    return label, "", ""


def get_label(sym: str, sub: str, unit: str) -> str:
    """Get label."""
    if sym and sub and unit:
        return f"{sym}_{sub} ({unit})"
    return f"{sym} ({unit})" if sym and unit else sym


def get_latex(sym: str, sub: str, unit: str) -> str:
    """Get LaTeX label."""
    if sub:
        sym = f"{sym}_{{{sub}}}"
    if unit:
        sym = rf"{sym}\ \left({unit}\right)"
    return rf"$\mathsf{{{sym}}}$"


@dataclass
class Col:
    """Column transformation."""

    src: str
    dst: str = ""
    unit: str = ""
    dst_unit: str = ""
    scale: float = 1
    latex: str = ""
    df: str = ""
    ylabel: str = ""

    def __call__(self) -> Any:
        return self.latex

    def __post_init__(self):
        src_sym, src_sub, src_unit = get_parts(self.src)
        self.unit = get_unit(self.unit or src_unit)

        self.dst = self.dst or get_label(src_sym, src_sub, self.unit)
        dst_sym, dst_sub, dst_unit = get_parts(self.dst)
        self.dst_unit = get_unit(self.dst_unit) or dst_unit or self.unit
        self.dst = get_label(dst_sym, dst_sub, self.dst_unit)
        self.ylabel = get_latex(dst_sym, "", self.dst_unit)

        self.latex = self.latex or get_latex(dst_sym, dst_sub, self.dst_unit)
        self.df = self.df or self.dst


class Conversion(TypedDict):
    """Scalar conversion between units."""

    old_unit: str
    new_unit: str
    scale: float


M_TO_MM = Conversion(old_unit="m", new_unit="mm", scale=1000)


class Columns(BaseModel):
    """Columns."""

    frame: Col = Col("frame", "Frame #")


def transform_cols(df: DataFrame, cols: list[Col], drop: bool = True) -> DataFrame:
    """Transform dataframe columns."""
    df = df.assign(**{
        col.dst: df[col.src] if col.scale == 1 else df[col.src] * col.scale
        for col in cols
    })
    return df[[col.dst for col in cols]] if drop else df


def get_cols(cols_model: BaseModel, meta: str) -> list[Col]:
    """Get columns."""
    cols = dict(cols_model)
    return list(
        chain.from_iterable(
            cols[field] if isinstance(cols[field], list) else [cols[field]]
            for field, info in cols_model.model_fields.items()
            if meta in info.metadata
        )
    )


class VideoDims(BaseModel):
    """Video dimensions."""

    y: Col = Col(Y, unit=PX)
    x: Col = Col(X, unit=PX)


class ThermalCols(BaseModel):
    """Thermal columns."""

    time: Annotated[Col, IDX, SRC, DST] = Col("time", "Time")
    time_elapsed: Annotated[Col, DST] = Col("t", unit="s")
    time_elapsed_min: Col = Col("t", unit="s", dst_unit="min", scale=1 / 60)

    water_temps: Annotated[list[Col], SRC, DST] = [
        Col("Tw3cal (C)", "T_w3"),
        Col("Tw4cal (C)", "T_w4"),
    ]
    water_temp: Annotated[Col, DST] = Col("T_w (C)")
    superheat: Annotated[Col, DST] = Col("ΔT_super (K)")
    subcool: Annotated[Col, DST] = Col("ΔT_sub (K)")

    base_temp: Annotated[Col, SRC, DST] = Col("T0cal (C)", "T_0")
    sample_temps: Annotated[list[Col], SRC, DST] = [
        Col("T1cal (C)", "T_1"),
        Col("T2cal (C)", "T_2"),
        Col("T3cal (C)", "T_3"),
        Col("T4cal (C)", "T_4"),
        Col("T5cal (C)", "T_5"),
    ]
    surface_temp: Annotated[Col, SRC, DST] = Col("T_s (C)")
    flux: Annotated[Col, DST] = Col("q'' (W/cm^2)", scale=1e-4)

    boiling: Annotated[Col, DST] = Col("T_sat (C)")

    @model_validator(mode="after")
    def validate_time(self) -> Self:
        """Validate time column."""
        if len(self.idx) > 1 or self.time != self.idx[0]:
            raise ValueError("Expected only one index column.")
        return self

    @property
    def idx(self) -> list[Col]:
        """All index columns."""
        return get_cols(self, IDX)

    @property
    def sources(self) -> list[Col]:
        """All source columns."""
        return get_cols(self, SRC)

    @property
    def dests(self) -> list[Col]:
        """All destination columns."""
        return get_cols(self, DST)


class Constants(BaseModel):
    day: str = "2024-07-18"
    time: str = "17-44-35"
    thermal_cols: ThermalCols = ThermalCols()
    video_dims: VideoDims = VideoDims()
    nb_slicer_patterns: dict[str, Slicers] = {
        r".+": {FRAME: first_slicer(n=10, step=100)}
    }
    """Slicer patterns representing a small subset of frames."""

    @property
    def sample(self) -> str:
        """Sample to process."""
        return f"{self.day}T{self.time}"

    @property
    def nb_include_patterns(self) -> list[str]:
        """Include patterns for a single sample."""
        return [rf"^.*{self.sample}.*$"]

    @property
    def include_patterns(self) -> list[str]:
        """Include patterns."""
        return [rf"^.*{self.day}.*$"]


const = Constants()


class Params(stages.Params[Deps_T, Outs_T], Generic[Deps_T, Outs_T]):
    """Stage parameters for `e230920`."""

    deps: Deps_T
    """Stage dependencies."""
    outs: Outs_T
    """Stage outputs."""
    sample: str = const.sample
    """Sample to process."""
    include_patterns: list[str] = const.include_patterns
    """Include patterns."""


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


def save_df(df: DataFrame, path: Path | str, key: str | None = None):
    """Save data frame to a compressed HDF5 file."""
    path = Path(path)
    df.to_hdf(path, key=key or path.stem, complib="zlib", complevel=9)


def callbacks(
    future: Future[DfNbOuts], /, callbacks: Iterable[Callable[[Future[DfNbOuts]], None]]
):
    """Apply a series of done callbacks to the future."""
    for callback in callbacks:
        callback(future)


def save_plots(figs: Iterable[Figure], plots: Path):
    """Save a DataFrame to HDF5 format."""
    for i, fig in enumerate(figs):
        fig.savefig(
            plots / f"{plots.stem}_{i}.png"  # pyright: ignore[reportArgumentType]
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
    cols = numpy.any(dilated, axis=0)
    rows = numpy.any(dilated, axis=1)
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
