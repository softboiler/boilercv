"""Plot operations."""

from pathlib import Path

from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.colors import ListedColormap, Normalize
from pandas import CategoricalDtype, DataFrame
from pydantic import BaseModel
from seaborn import color_palette


def get_cat_colorbar(
    ax: Axes, col: str, palette: str, data: DataFrame, alpha: float = 1.0
) -> tuple[list[tuple[float, float, float]], DataFrame]:
    """Get categorical colorbar."""
    if isinstance(data[col].dtype, CategoricalDtype):
        data[col] = data[col].cat.remove_unused_categories()
        num_colors = len(data[col].cat.categories)
    else:
        num_colors = data[col].nunique()
    p = ListedColormap(color_palette(palette, num_colors))
    mappable = ScalarMappable(cmap=p, norm=Normalize(0, num_colors))
    mappable.set_array([])
    colorbar = ax.figure.colorbar(ax=ax, mappable=mappable, label=col, alpha=alpha)  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess], CI
    colorbar.set_ticks([])
    return p.colors, data  # pyright: ignore[reportAttributeAccessIssue]


def save_plots(plots: BaseModel, path: Path, suffix: str = ""):
    """Save a DataFrame to HDF5 format."""
    for name, fig in plots.model_dump().items():
        fig.savefig(
            path / ("_".join([f"{name}", *([suffix] if suffix else [])]) + ".png")
        )
