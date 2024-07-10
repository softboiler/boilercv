"""Fill bubble contours."""

from loguru import logger
from numpy import empty, uint8
from pandas import DataFrame
from xarray import zeros_like

from boilercv.data import VIDEO
from boilercv.images.cv import draw_contours
from boilercv.types import ArrInt
from boilercv_pipeline import PREVIEW
from boilercv_pipeline.captivate.previews import view_images
from boilercv_pipeline.examples import EXAMPLE_NUM_FRAMES, EXAMPLE_VIDEO_NAME
from boilercv_pipeline.sets import get_contours_df, get_dataset

TRY_EMPTY = False


def main():  # noqa: D103
    if TRY_EMPTY:
        all_contours = empty((0, 4))
        df = DataFrame(
            all_contours, columns=["frame", "contour", "ypx", "xpx"]
        ).set_index(["frame", "contour"])
    else:
        df = get_contours_df(EXAMPLE_VIDEO_NAME)
    ds = zeros_like(get_dataset(EXAMPLE_VIDEO_NAME, EXAMPLE_NUM_FRAMES), dtype=uint8)
    video = ds[VIDEO]
    if not df.empty:
        for frame_num, frame in enumerate(video):
            contours: list[ArrInt] = list(  # type: ignore  # pyright 1.1.333
                df.loc[frame_num, :].groupby("contour").apply(lambda grp: grp.values)
            )
            video[frame_num, :, :] = draw_contours(frame.values, contours)
    if PREVIEW:
        view_images(video)


if __name__ == "__main__":
    logger.info("Start filling contours")
    main()
    logger.info("Finish filling contours")
