"""Examples, experiments, and demonstrations."""

from xarray import open_dataset

from boilercv.data import VIDEO
from boilercv.types import DA
from boilercv_pipeline.models.paths import paths

EXAMPLE_NUM_FRAMES = 500
EXAMPLE_VIDEO_NAME = "2022-11-30T13-41-00"
EXAMPLE_CONTOURS = paths.examples / f"{EXAMPLE_VIDEO_NAME}.h5"
# TODO: Source the ROI from the dataset.
EXAMPLE_ROI = paths.examples / f"{EXAMPLE_VIDEO_NAME}_roi.yaml"


def get_images() -> DA:
    """Get images."""
    with open_dataset(paths.examples / f"{EXAMPLE_VIDEO_NAME}.nc") as ds:
        return ds[VIDEO].sel(frame=slice(None, EXAMPLE_NUM_FRAMES))


EXAMPLE_VIDEO = get_images()
EXAMPLE_FRAME_LIST = list(EXAMPLE_VIDEO.values)
