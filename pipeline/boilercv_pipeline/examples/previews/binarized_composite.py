"""Overlay detected bubbles on the binarized stage."""

from boilercv.data import VIDEO
from boilercv.images import scale_bool
from boilercv_pipeline import PREVIEW, WRITE
from boilercv_pipeline.captivate import FRAMERATE_CONT
from boilercv_pipeline.captivate.captures import write_video
from boilercv_pipeline.captivate.previews import view_images
from boilercv_pipeline.config import default
from boilercv_pipeline.examples.previews import _EXAMPLE, _NUM_FRAMES
from boilercv_pipeline.previews import compose_da
from boilercv_pipeline.sets import get_dataset


def main():  # noqa: D103
    source = get_dataset(_EXAMPLE, _NUM_FRAMES, stage="sources")[VIDEO]
    bubbles = get_dataset(_EXAMPLE, _NUM_FRAMES, stage="filled")[VIDEO]
    highlighted_bubbles = compose_da(source, scale_bool(bubbles)).transpose(
        "frame", "ypx", "xpx", "channel"
    )
    if PREVIEW:
        view_images(bubbles.isel(frame=0))
        view_images(highlighted_bubbles, framerate=FRAMERATE_CONT)
    if WRITE:
        write_video(default.params.paths.media / "binarized", source)
        write_video(default.params.paths.media / "bubbles", bubbles, preview_frame=True)
        write_video(
            default.params.paths.media / "binarized_highlighted", highlighted_bubbles
        )


if __name__ == "__main__":
    main()
