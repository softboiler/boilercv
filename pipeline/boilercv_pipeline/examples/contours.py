"""Get bubble contours."""

from cv2 import CHAIN_APPROX_SIMPLE, bitwise_not
from numpy import newaxis, repeat

from boilercv.colors import BLUE
from boilercv.data import VIDEO, islice
from boilercv.images import scale_bool
from boilercv.images.cv import draw_contours
from boilercv.types import ArrInt, Img
from boilercv_pipeline import PREVIEW
from boilercv_pipeline.captivate.previews import view_images
from boilercv_pipeline.examples import (
    EXAMPLE_CONTOURS,
    EXAMPLE_NUM_FRAMES,
    EXAMPLE_VIDEO_NAME,
)
from boilercv_pipeline.sets import get_dataset
from boilercv_pipeline.stages.find_contours import get_all_contours


def main():  # noqa: D103
    ds = get_dataset(EXAMPLE_VIDEO_NAME, EXAMPLE_NUM_FRAMES)
    video = ds[VIDEO]
    df = get_all_contours(
        bitwise_not(scale_bool(video.values)), method=CHAIN_APPROX_SIMPLE
    )
    df.to_hdf(EXAMPLE_CONTOURS, key="contours", complib="zlib", complevel=9)
    result: list[Img] = []
    for frame_num, frame in enumerate(video):
        contours: list[ArrInt] = list(  # pyright: ignore[reportAssignmentType]
            df.loc[islice[frame_num], :]  # pyright: ignore[reportArgumentType]
            .groupby("contour")
            .apply(lambda grp: grp.values)  # pyright: ignore[reportAttributeAccessIssue]
        )
        frame_color = repeat(scale_bool(frame.values)[:, :, newaxis], 3, axis=-1)
        result.append(draw_contours(frame_color, contours, thickness=2, color=BLUE))
    if PREVIEW:
        view_images(result)


if __name__ == "__main__":
    main()
