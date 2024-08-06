"""Preview detected regions on an image from the dataset."""

from xarray import open_dataset

from boilercv.colors import BLUE, GREEN, RED
from boilercv.data import ROI, VIDEO
from boilercv.images import overlay, scale_bool
from boilercv_pipeline import PREVIEW, WRITE
from boilercv_pipeline.captivate.captures import write_image
from boilercv_pipeline.captivate.previews import view_images
from boilercv_pipeline.config import default
from boilercv_pipeline.examples.detect_surface import find_boiling_surface
from boilercv_pipeline.examples.previews import _EXAMPLE
from boilercv_pipeline.sets import get_dataset


def main():  # noqa: D103
    ds = get_dataset(_EXAMPLE)
    gray = (
        open_dataset(default.params.paths.gray_preview)[VIDEO]
        .sel(video_name=_EXAMPLE)
        .values
    )
    roi = ds[ROI].values
    highlighted_roi = overlay(gray, scale_bool(roi), color=BLUE, alpha=0.2)

    surface, _ = find_boiling_surface(scale_bool(roi))
    highlighted_surface = overlay(
        highlighted_roi, scale_bool(surface), color=RED, alpha=1
    )

    filled = (
        open_dataset(default.params.paths.filled_preview)[VIDEO]
        .sel(video_name=_EXAMPLE)
        .values
    )
    highlighted_bubbles = overlay(
        highlighted_surface, scale_bool(filled), color=GREEN, alpha=0.4
    )

    if PREVIEW:
        view_images(highlighted_bubbles)
    if WRITE:
        write_image(default.params.paths.media / "roi", highlighted_roi)
        write_image(default.params.paths.media / "composite", highlighted_bubbles)


if __name__ == "__main__":
    main()
