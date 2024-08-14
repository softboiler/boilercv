"""Overlay detected bubbles on the gray stage."""

from boilercv.data import VIDEO
from boilercv.images import scale_bool
from boilercv_pipeline import PREVIEW, WRITE
from boilercv_pipeline.captivate import FRAMERATE_CONT
from boilercv_pipeline.captivate.captures import write_video
from boilercv_pipeline.captivate.previews import view_images
from boilercv_pipeline.examples.previews import _EXAMPLE, _NUM_FRAMES
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.previews import compose_da
from boilercv_pipeline.sets import get_dataset


def main():  # noqa: D103
    gray_source = get_dataset(_EXAMPLE, _NUM_FRAMES, stage="large_sources")[VIDEO]
    bubbles = get_dataset(_EXAMPLE, _NUM_FRAMES, stage="filled")[VIDEO]
    highlighted_bubbles = compose_da(gray_source, scale_bool(bubbles)).transpose(
        "frame", "ypx", "xpx", "channel"
    )
    if PREVIEW:
        view_images(highlighted_bubbles, framerate=FRAMERATE_CONT)
    if WRITE:
        path = paths.params.paths.media / "examples" / _EXAMPLE / "gray_highlighted"
        path.parent.mkdir(parents=True, exist_ok=True)
        write_video(path, highlighted_bubbles, preview_frame=True)


if __name__ == "__main__":
    main()
