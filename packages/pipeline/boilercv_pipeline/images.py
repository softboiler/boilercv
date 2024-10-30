"""Images."""

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path

import numpy
from boilercine import get_cine_attributes, get_cine_images
from matplotlib.axes import Axes
from matplotlib.pyplot import subplots
from numpy import where
from scipy.spatial.distance import euclidean

from boilercv.data import (
    FRAME,
    LENGTH,
    SAMPLE_DIAMETER_UM,
    TIME,
    TIMEZONE,
    UTC_TIME,
    VIDEO,
    XPX,
    YPX,
    YX,
    assign_ds,
)
from boilercv.data.models import Dimension
from boilercv.images import scale_bool
from boilercv.images.cv import Op, Transform, transform
from boilercv.types import DA, DS, ArrInt, Img
from boilercv_pipeline.models.header import CineHeader
from boilercv_pipeline.types import Slicer2D


def prepare_dataset(
    cine_source: Path,
    num_frames: int | None = None,
    start_frame: int = 0,
    crop: Slicer2D | None = None,
) -> tuple[CineHeader, DS]:
    """Prepare a dataset from a CINE."""
    # Header
    header, utc_arr = get_cine_attributes(
        cine_source, TIMEZONE, num_frames, start_frame
    )
    header = CineHeader(**asdict(header))

    # Dimensions
    frame_dim = Dimension(dim=FRAME, long_name="Frame number")
    time = Dimension(
        parent_dim=frame_dim.dim,
        dim=TIME,
        long_name="Time elapsed",
        units="s",
        original_units="ns",
        original_coords=(utc_arr - utc_arr[0]).astype(float),
        scale=1e-9,
    )
    utc = Dimension(
        parent_dim=frame_dim.dim, dim=UTC_TIME, long_name="UTC time", coords=utc_arr
    )

    # Dataset
    images = get_cine_images(cine_source, num_frames, start_frame)
    ds = assign_ds(
        name=VIDEO,
        long_name="High-speed video data",
        units="Pixel intensity",
        fixed_dims=(frame_dim,),
        dims=(
            Dimension(dim=YPX, long_name="Height", units="px"),
            Dimension(dim=XPX, long_name="Width", units="px"),
        ),
        fixed_secondary_dims=(time, utc),
        data=[i[*tuple(slice(*c) for c in crop)] for i in images]
        if crop
        else list(images),
    )

    # Return header and dataset
    return header, ds


# * -------------------------------------------------------------------------------- * #
# * SECONDARY LENGTH DIMENSIONS


def assign_length_dims(dataset: DS, roi: ArrInt) -> DS:
    """Assign length scales to "x" and "y" coordinates."""
    images = dataset[VIDEO]
    parent_dim_units = "px"
    pixels = euclidean(*iter(roi))
    um_per_px = SAMPLE_DIAMETER_UM / pixels
    y = get_length_dims(parent_dim_units, YX[0], "Height", um_per_px, images)
    x = get_length_dims(parent_dim_units, YX[1], "Width", um_per_px, images)
    images = y.assign_to(images)
    images = x.assign_to(images)
    return dataset


def get_length_dims(
    parent_dim_units: str, dim: str, long_name: str, scale: float, images: DA
) -> Dimension:
    """Get a length scale."""
    parent_dim = f"{dim}{parent_dim_units}"
    return Dimension(
        parent_dim=f"{dim}{parent_dim_units}",
        dim=dim,
        long_name=long_name,
        units=LENGTH,
        original_units=parent_dim_units,
        original_coords=images[parent_dim].values,
        scale=scale,
    )


def get_image_boundaries(img) -> tuple[tuple[int, int], tuple[int, int]]:
    """Get the boundaries of an image."""
    dilated = transform(scale_bool(img), Transform(Op.dilate, 12))
    cols = numpy.any(dilated, axis=0)
    rows = numpy.any(dilated, axis=1)
    ylim = tuple(where(rows)[0][[0, -1]])
    xlim = tuple(where(cols)[0][[0, -1]])
    return ylim, xlim


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


def plot_composite_da(video: DA, ax: Axes | None = None) -> Axes:
    """Compose a video-like data array and highlight the first frame."""
    first_frame = video.sel(frame=0).values
    composite_video = video.max("frame").values
    with bounded_ax(composite_video, ax) as ax:
        ax.imshow(~first_frame, alpha=0.6)
        ax.imshow(~composite_video, alpha=0.2)
    return ax


def crop_image(img, ylim, xlim):
    """Crop an image to the specified boundaries."""
    return img[ylim[0] : ylim[1] + 1, xlim[0] : xlim[1] + 1]
