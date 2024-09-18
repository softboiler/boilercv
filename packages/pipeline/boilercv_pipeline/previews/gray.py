"""Preview the grayscale stage."""

from xarray import open_dataset

from boilercv.data import VIDEO
from boilercv.types import DA
from boilercv_pipeline import PREVIEW
from boilercv_pipeline.captivate import FRAMERATE_PREV
from boilercv_pipeline.captivate.previews import view_images
from boilercv_pipeline.previews import draw_text_da
from boilercv_pipeline.sets import ROOTED_PATHS


def main(preview: bool = PREVIEW) -> DA:  # noqa: D103
    with open_dataset(ROOTED_PATHS.gray_preview) as ds:
        da = draw_text_da(ds[VIDEO])
    if preview:
        view_images(da, framerate=FRAMERATE_PREV)
    return da


if __name__ == "__main__":
    main()
