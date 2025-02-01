"""Overlay detected bubbles on the image."""

from boilercv.data import VIDEO
from boilercv.images import scale_bool
from boilercv.types import DA
from boilercv_pipeline import PREVIEW, WRITE
from boilercv_pipeline.captivate import FRAMERATE_PREV
from boilercv_pipeline.captivate.captures import write_video
from boilercv_pipeline.captivate.previews import view_images
from boilercv_pipeline.previews import compose_da, draw_text_da, get_preview
from boilercv_pipeline.sets import ROOTED_PATHS


def main(preview: bool = PREVIEW) -> DA:
    gray = get_preview(ROOTED_PATHS.gray_preview)
    filled = get_preview(ROOTED_PATHS.filled_preview)
    composed = draw_text_da(
        compose_da(gray[VIDEO], scale_bool(filled[VIDEO])).transpose(
            "video_name", "ypx", "xpx", "channel"
        )
    )
    if preview:
        view_images(composed, framerate=FRAMERATE_PREV)
    if WRITE:
        write_video(
            ROOTED_PATHS.media / "examples" / "composite",
            composed,
            framerate=FRAMERATE_PREV,
        )
    return composed


if __name__ == "__main__":
    main()
