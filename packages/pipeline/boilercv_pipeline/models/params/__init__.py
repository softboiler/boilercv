"""Pipeline stages model."""

from __future__ import annotations

from collections.abc import Iterable
from contextlib import contextmanager
from typing import Generic, Self

import matplotlib
from context_models import CONTEXT
from context_models.validators import context_model_validator
from IPython.display import Markdown, display
from matplotlib.axes import Axes
from numpy import set_printoptions
from pandas import DataFrame, MultiIndex, RangeIndex, Series, options
from pydantic import BaseModel
from seaborn import move_legend, set_theme

from boilercv_pipeline.models.column import Col
from boilercv_pipeline.models.column.types import Ps
from boilercv_pipeline.models.contexts import DVC
from boilercv_pipeline.models.contexts.types import BoilercvPipelineValidationInfo
from boilercv_pipeline.models.params.types import (
    Data_T,
    Deps_T,
    DfOrS_T,
    Outs_T,
    Preview,
)
from boilercv_pipeline.models.path import get_boilercv_pipeline_config
from boilercv_pipeline.models.stage import Stage


class Constants(BaseModel):
    """Parameter constants."""

    scale: float = 1.3
    paper_scale: float = 1.0
    precision: int = 3
    display_rows: int = 12


const = Constants()


def set_display_options(
    scale: float = const.scale,
    precision: int = const.precision,
    display_rows: int = const.display_rows,
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
        font_scale=scale,
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


class Params(Stage, Generic[Deps_T, Outs_T]):
    """Stage parameters."""

    deps: Deps_T
    """Stage dependencies."""
    outs: Outs_T
    """Stage outputs."""

    # ? Format parameters and properties

    scale: float = const.scale
    """Plot scale."""
    marker_scale: float = 20
    """Marker scale."""
    precision: int = const.precision
    """Number precision."""
    display_rows: int = const.display_rows
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

    def set_display_options(
        self,
        scale: float | None = None,
        precision: int | None = None,
        display_rows: int | None = None,
    ):
        """Set display options."""
        set_display_options(
            scale or self.scale,
            precision or self.precision,
            display_rows or self.display_rows,
        )

    def move_legend(
        self, ax: Axes, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3
    ):
        """Move legend."""
        move_legend(ax, loc=loc, bbox_to_anchor=bbox_to_anchor, ncol=ncol)

    def preview(
        self,
        df: DfOrS_T,
        cols: Iterable[Col] | None = None,
        index: Col | None = None,
        f: Preview[Ps] = head,
        ncol: int = 0,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> DfOrS_T:
        """Preview a dataframe in the notebook."""
        if df.empty:
            display(df)
            return df
        _fmt = self.floatfmt
        if isinstance(df, Series):
            display_markdown(
                DataFrame(df[:ncol] if ncol else df)
                .pipe(f, *args, **kwds)
                .rename_axis("Parameter")
                .rename(columns={0: "Value"})
            )
            return df

        _df = df.pipe(f, *args, **kwds)
        if cols:
            _fmt = tuple(c.fmt or self.floatfmt for c in cols)
            _cols = (
                [c() for c in cols if c() in _df.columns] if cols else list(_df.columns)
            )
        else:
            _fmt = self.floatfmt
            _cols = list(_df.columns)
        _cols = _cols[:ncol] if ncol else _cols

        if index:
            display_markdown(
                _df.reset_index(drop=_df.empty).set_index(index())[_cols],
                floatfmt=_fmt,  # pyright: ignore[reportArgumentType]
            )
            return df
        if isinstance(_df.index, MultiIndex):
            display_markdown(_df[_cols], floatfmt=_fmt)  # pyright: ignore[reportArgumentType]
            return df
        if _df.index.name and not isinstance(_df.index, RangeIndex):
            display_markdown(_df[_cols], floatfmt=_fmt)  # pyright: ignore[reportArgumentType]
            return df
        _index = _cols.pop(0)
        display_markdown(
            _df.reset_index(drop=_df.empty).set_index(_index)[_cols],
            floatfmt=_fmt,  # pyright: ignore[reportArgumentType]
        )
        return df

    @classmethod
    def hide(cls):
        """Hide unsuppressed output in notebook cells."""
        display()

    @contextmanager
    def display_options(
        self,
        scale: float = const.scale,
        precision: int = const.precision,
        display_rows: int = const.display_rows,
    ):
        """Display options."""
        try:
            self.set_display_options(scale, precision, display_rows)
            yield
        finally:
            self.set_display_options()


class DataParams(Params[Deps_T, Outs_T], Generic[Deps_T, Outs_T, Data_T]):
    """Stage parameters."""

    model_config = get_boilercv_pipeline_config()

    @context_model_validator(mode="after")
    def dvc_validate_data(self, info: BoilercvPipelineValidationInfo) -> Self:
        """Extend stage plots in `dvc.yaml`."""
        if (
            info.field_name != CONTEXT
            and (dvc := info.context.get(DVC))
            and dvc.plot_dir
            and not dvc.stage.plots
        ):
            dvc.stage.plots.extend(
                sorted(
                    (dvc.plot_dir / f"{name}.png").as_posix() for name in dvc.plot_names
                )
            )
            dvc.plot_dir = None
            dvc.plot_names.clear()
        return self

    data: Data_T
    """Stage data."""
