"""Save the ROI to a legacy YAML format."""

from warnings import warn

from cv2 import CHAIN_APPROX_SIMPLE

from boilercv.data import ROI, apply_to_img_da
from boilercv.images import scale_bool
from boilercv.images.cv import find_contours, get_wall
from boilercv.types import DA
from boilercv_pipeline.captivate.previews import save_roi
from boilercv_pipeline.examples import EXAMPLE_ROI, EXAMPLE_VIDEO_NAME
from boilercv_pipeline.sets import get_dataset


def main():
    ds = get_dataset(EXAMPLE_VIDEO_NAME)
    roi = ds[ROI]
    wall: DA = apply_to_img_da(get_wall, scale_bool(roi), name="wall")
    contours = find_contours(scale_bool(wall.values), method=CHAIN_APPROX_SIMPLE)
    if len(contours) > 1:
        warn("More than one contour found when searching for the ROI.", stacklevel=1)
    save_roi(contours[0], EXAMPLE_ROI)


if __name__ == "__main__":
    main()
