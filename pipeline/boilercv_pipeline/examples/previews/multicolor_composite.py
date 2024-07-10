"""Overlay detected bubbles on the gray stage."""

from itertools import cycle

from cv2 import COLOR_BGR2RGB, COLOR_GRAY2BGR
from matplotlib.pyplot import show
from numpy import zeros_like
from seaborn import color_palette, palplot

from boilercv.data import VIDEO
from boilercv.images import overlay
from boilercv.images.cv import convert_image, draw_contours
from boilercv.types import ArrInt
from boilercv_pipeline import DEBUG, PREVIEW, WRITE
from boilercv_pipeline.captivate.captures import write_image
from boilercv_pipeline.captivate.previews import view_images
from boilercv_pipeline.examples.previews import _EXAMPLE
from boilercv_pipeline.models.params import PARAMS
from boilercv_pipeline.sets import get_contours_df, get_dataset

_NUM_FRAMES = 1

_PALETTE = [c for c in color_palette("Set1") if not c[0] == c[1] == c[2]]
_PALETTE_CV = [(int(255 * c[2]), int(255 * c[1]), int(255 * c[0])) for c in _PALETTE]


def main():  # noqa: D103
    frame = _NUM_FRAMES - 1
    gray = (
        get_dataset(_EXAMPLE, _NUM_FRAMES, stage="large_sources")[VIDEO]
        .isel(frame=frame)
        .values
    )
    contours: list[ArrInt] = list(  # pyright: ignore[reportAssignmentType]
        get_contours_df(_EXAMPLE)
        .loc[frame, :]
        .groupby("contour")
        .apply(lambda grp: grp.values)
    )
    highlighted = zeros_like(convert_image(gray, COLOR_GRAY2BGR))
    for contour, color in zip(contours, cycle(_PALETTE_CV), strict=False):
        highlighted = draw_contours(highlighted, [contour], color=color)
    highlighted = convert_image(highlighted, COLOR_BGR2RGB)
    composed = overlay(gray, highlighted, alpha=0.7)
    if PREVIEW:
        if DEBUG:
            palplot(_PALETTE)
        show()
        view_images(composed)
    if WRITE:
        path = PARAMS.paths.media / "examples" / _EXAMPLE / "multicolor"
        path.parent.mkdir(parents=True, exist_ok=True)
        write_image(path, composed)


if __name__ == "__main__":
    main()
