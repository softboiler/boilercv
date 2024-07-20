"""Video dataset model."""

from dataclasses import asdict
from pathlib import Path

from boilercine import get_cine_attributes, get_cine_images
from scipy.spatial.distance import euclidean
from xarray import DataArray

from boilercv.data import (
    FRAME,
    HEADER,
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
from boilercv.types import DA, DS, ArrInt
from boilercv_pipeline.types import Slicer2D


def prepare_dataset(
    cine_source: Path,
    num_frames: int | None = None,
    start_frame: int = 0,
    crop: Slicer2D | None = None,
) -> DS:
    """Prepare a dataset from a CINE."""
    # Header
    header, utc_arr = get_cine_attributes(
        cine_source, TIMEZONE, num_frames, start_frame
    )
    header_da = DataArray(name=HEADER, attrs=asdict(header))

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
    ds[header_da.name] = header_da
    return ds


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
