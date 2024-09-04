"""Plot operations."""

from pathlib import Path
from typing import Any

from cmasher import get_sub_cmap
from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Colormap, Normalize
from matplotlib.figure import Figure
from pandas import CategoricalDtype, DataFrame


def get_first_from_palette(palette: Any, n: int) -> Colormap:
    """Get the first `n` colors from a palette."""
    return get_sub_cmap(
        palette, start=0, stop=n / (getattr(palette, "N", None) or len(palette)), N=n
    )


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


def save_plots(figs: dict[str, Figure], plots: Path):
    """Save a DataFrame to HDF5 format."""
    for name, fig in figs.items():
        fig.savefig(plots / f"{name}.png")  # pyright: ignore[reportArgumentType]
