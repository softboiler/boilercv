"""Get bubble contours."""

from cappa.base import invoke
from cv2 import CHAIN_APPROX_SIMPLE, bitwise_not
from loguru import logger
from numpy import empty, insert, vstack
from pandas import DataFrame
from tqdm import tqdm

from boilercv.data import VIDEO
from boilercv.images import scale_bool
from boilercv.images.cv import find_contours
from boilercv.types import DF, Vid
from boilercv_pipeline.models.generated.stages.find_contours import FindContours
from boilercv_pipeline.sets import get_dataset, get_unprocessed_destinations


def main(args: FindContours):  # noqa: D103
    logger.info("Start finding contours")
    destinations = get_unprocessed_destinations(
        args.outs.contours,
        names=[source.stem for source in sorted(args.deps.sources.iterdir())],
        ext="h5",
    )
    for source_name, destination in tqdm(destinations.items()):
        video = bitwise_not(scale_bool(get_dataset(source_name)[VIDEO].values))
        df = get_all_contours(video, method=CHAIN_APPROX_SIMPLE)
        df.to_hdf(destination, key="contours", complib="zlib", complevel=9)
    logger.info("Finish finding contours")


def get_all_contours(video: Vid, method) -> DF:
    """Get all contours in a video.

    Produces a dataframe with a multi-index of the video frame and contour number, and
    two columns indicating the "y" and "x" pixel locations of contour vertices.

    Args:
        video: Video to get contours from.
        method: The contour approximation method to use.
    """
    # This nested, pure-numpy approach is a bit hard to follow, but it is much faster
    # than the more readable approach of building and concatenating dataframes. The
    # overhead of dataframe creation over ~6000 frames is significant.
    try:
        # Vertically stack the contours detected in each frame
        all_contours = vstack(
            # For each frame in the video...
            [
                # Compose two columns, the frame number and the contours
                insert(
                    axis=1,  # Insert column-wise
                    obj=0,  # Insert at the beginning, e.g. prepend
                    values=frame_num,
                    # Vertically stack the pixel locations of each contour
                    arr=vstack(
                        # For each contour in the frame...
                        [
                            # Prepend the contour number to the contour locations
                            insert(axis=1, obj=0, values=cont_num, arr=contour)
                            for cont_num, contour in enumerate(
                                find_contours(image, method)
                            )
                        ]
                    ),
                )
                for frame_num, image in enumerate(video)
            ]
        )
    except ValueError:
        # Some frames may have no contours. Signal this with an empty array
        logger.warning("No contours found in this frame.")
        all_contours = empty((0, 4))
    # Build the dataframe at the very end to avoid the overhead
    return DataFrame(
        all_contours, columns=["frame", "contour", "ypx", "xpx"]
    ).set_index(["frame", "contour"])


if __name__ == "__main__":
    invoke(FindContours)
