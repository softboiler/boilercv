"""Pipeline stages model."""

from __future__ import annotations

from collections.abc import Iterable
from contextlib import contextmanager
from typing import Annotated as Ann
from typing import Generic

import matplotlib
from cappa.arg import Arg
from IPython.display import Markdown, display
from matplotlib.axes import Axes
from numpy import set_printoptions
from pandas import DataFrame, options
from pydantic import BaseModel, Field
from seaborn import move_legend, set_theme

from boilercv_pipeline.models.column import Col
from boilercv_pipeline.models.column.types import Ps
from boilercv_pipeline.models.params.types import Data_T, Deps_T, Outs_T, Preview
from boilercv_pipeline.models.stage import Stage


def set_display_options(
    font_scale: float = 1.3, precision: int = 3, display_rows: int = 12
):
    """Set display options."""
    float_spec = f"#.{precision}g"
    # The triple curly braces in the f-string allows the format function to be
    # dynamically specified by a given float specification. The intent is clearer this
    # way, and may be extended in the future by making `float_spec` a parameter.
    options.display.float_format = f"{{:{float_spec}}}".format
    options.display.min_rows = options.display.max_rows = display_rows
    set_printoptions(precision=precision)
    set_theme(
        context="notebook",
        style="whitegrid",
        palette="deep",
        font="sans-serif",
        font_scale=font_scale,
    )
    matplotlib.rcParams |= {
        # * Figure
        "figure.autolayout": True,
        # * Images (e.g. imshow)
        "image.cmap": "gray",
        # * Legend format
        # ? Make legend opaque
        "legend.framealpha": None,
        # * Saving figures
        # ? Fix whitespace around axes
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.2,
        # ? Transparent figure background, leave axes white
        "savefig.facecolor": (1, 1, 1, 0),
        # ? DPI for saving figures only
        "savefig.dpi": 600,
        # ! Also hide title
        # "axes.titlepad": 0,
        # "axes.titlesize": "xx-small",
        # "axes.titlecolor": "#00000000",
    }


def display_markdown(df: DataFrame, floatfmt: str = "#.3g"):
    """Render dataframes as Markdown, facilitating MathJax rendering.

    Notes
    -----
    https://github.com/jupyter-book/jupyter-book/issues/1501#issuecomment-2301641068
    """
    display(Markdown(df.to_markdown(floatfmt=floatfmt)))


def head(df: DataFrame) -> DataFrame:  # noqa: D103
    return df.head()


def get_floatfmt(precision: int = 3) -> str:
    """Get floating number format at given precision."""
    return f"#.{precision}g"


class Format(BaseModel):
    """Plotting parameters."""

    scale: float = 1.3
    """Plot scale."""
    marker_scale: float = 20
    """Marker scale."""
    precision: int = 3
    """Number precision."""
    display_rows: int = 12
    """Number of rows to display in data frames."""

    @property
    def size(self) -> float:
        """Marker size."""
        return self.scale * self.marker_scale

    @property
    def floatfmt(self) -> str:
        """Floating number format."""
        return get_floatfmt(self.precision)

    @property
    def font_scale(self) -> float:
        """Font scale."""
        return self.scale

    def set_display_options(self):
        """Set display options."""
        set_display_options(self.font_scale, self.precision, self.display_rows)

    def move_legend(
        self, ax: Axes, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3
    ):
        """Move legend."""
        move_legend(ax, loc=loc, bbox_to_anchor=bbox_to_anchor, ncol=ncol)

    def preview(
        self,
        df: DataFrame,
        cols: Iterable[Col] | None = None,
        index: Col | None = None,
        f: Preview[Ps] = head,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> DataFrame:
        """Preview a dataframe in the notebook."""
        _fmt = self.floatfmt
        if cols:
            _fmt = tuple(c.fmt or self.floatfmt for c in cols)
            _cols = [c() for c in cols] if cols else list(df.columns)
        else:
            _fmt = self.floatfmt
            _cols = list(df.columns)
        _index: str = index or _cols.pop(0)  # pyright: ignore[reportAssignmentType]
        display_markdown(
            df.pipe(f, *args, **kwds).set_index(_index)[_cols],
            floatfmt=_fmt,  # pyright: ignore[reportArgumentType]
        )
        return df

    @classmethod
    def hide(cls):
        """Hide unsuppressed output in notebook cells."""
        display()

    @contextmanager
    def display_options(self, other: Format):
        """Display options."""
        try:
            other.set_display_options()
            yield
        finally:
            self.set_display_options()


class Params(Stage, Generic[Deps_T, Outs_T]):
    """Stage parameters."""

    deps: Deps_T
    """Stage dependencies."""
    outs: Outs_T
    """Stage outputs."""
    format: Ann[Format, Arg(hidden=True)] = Field(default_factory=Format)
    """Format parameters."""

    def model_post_init(self, _context):
        """Unset kinds to avoid re-checking them."""
        self.context["boilercv_pipeline"].kinds = {}


class DataParams(Params[Deps_T, Outs_T], Generic[Deps_T, Outs_T, Data_T]):
    """Stage parameters."""

    data: Data_T
    """Stage data."""
