"""Stage models."""

from contextlib import contextmanager
from typing import Generic, TypeAlias

import matplotlib
from IPython.display import display
from matplotlib.axes import Axes
from numpy import set_printoptions
from pandas import options
from pydantic import BaseModel, Field
from seaborn import move_legend, set_theme

from boilercv_pipeline.models.path import BoilercvPipelineCtxDict
from boilercv_pipeline.models.paths.types import Deps_T, Outs_T, Stage, StagePaths


def set_display_options(
    font_scale: float = 1.3, precision: int = 3, display_rows: int = 12
):
    """Set display options."""
    float_spec = f".{precision}g"
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


class Format(BaseModel):
    """Plotting parameters."""

    scale: float = 1.3
    """Plot scale."""
    marker_scale: float = 20
    """Marker scale."""
    precision: int = 4
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
        return f"#.{self.precision}g"

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


@contextmanager
def display_options(orig: Format, new: Format):
    """Display options."""
    try:
        new.set_display_options()
        yield
    finally:
        orig.set_display_options()


class Params(Stage, Generic[Deps_T, Outs_T]):
    """Stage parameters."""

    deps: Deps_T
    """Stage dependencies."""
    outs: Outs_T
    """Stage outputs."""
    format: Format = Field(default_factory=Format)
    """Format parameters."""

    @classmethod
    def context_post_init(  # pyright: ignore[reportIncompatibleMethodOverride]
        cls, context: BoilercvPipelineCtxDict
    ) -> BoilercvPipelineCtxDict:
        """Unset kinds to avoid re-checking them."""
        context["boilercv_pipeline"].kinds = {}
        return context

    @classmethod
    def hide(cls):
        """Hide unsuppressed output in notebook cells."""
        display()


AnyParams: TypeAlias = Params[StagePaths, StagePaths]
