"""Preview results."""

from pathlib import Path

from xarray import Dataset, apply_ufunc, open_dataset

from boilercv.colors import RED
from boilercv.data import VIDEO, YX_PX, identity_da
from boilercv.images import draw_text, overlay
from boilercv.types import DA, DS
from boilercv_pipeline import DEBUG
from boilercv_pipeline.sets import slice_frames

_NUM_FRAMES = 100 if DEBUG else 0


def get_preview(path: Path) -> DS:
    """Get a preview dataset.

    Args:
        path: Path to dataset.
    """
    with open_dataset(path) as ds:
        return Dataset({VIDEO: ds[VIDEO][slice_frames(_NUM_FRAMES)]})


def draw_text_da(da: DA) -> DA:
    """Draw text on images in a data array."""
    frames_dim = str(da.dims[0])
    if da.ndim == 4:
        # We have a color video
        return apply_ufunc(
            draw_text,
            da,
            identity_da(da, frames_dim),
            input_core_dims=([*YX_PX, "channel"], []),
            output_core_dims=([*YX_PX, "channel"],),
            vectorize=True,
        )
    else:
        return apply_ufunc(
            draw_text,
            da,
            identity_da(da, frames_dim),
            input_core_dims=(YX_PX, []),
            output_core_dims=(YX_PX,),
            vectorize=True,
        )


def compose_da(da_image: DA, da_overlay: DA, color: tuple[int, int, int] = RED) -> DA:
    """Draw text on images in a data array.

    Args:
        da_image: Image data array.
        da_overlay: Overlay data array.
        color: Color for the overlay.
    """
    return apply_ufunc(
        overlay,
        da_image,
        da_overlay,
        input_core_dims=(YX_PX, YX_PX),
        output_core_dims=([*YX_PX, "channel"],),
        vectorize=True,
        kwargs=dict(color=color),
    )
