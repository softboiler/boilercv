from cappa.base import invoke
from cv2 import CHAIN_APPROX_SIMPLE, bitwise_not
from loguru import logger
from tqdm import tqdm

from boilercv.data import VIDEO
from boilercv.images import scale_bool
from boilercv_pipeline.sets import get_dataset, get_unprocessed_destinations
from boilercv_pipeline.stages.common.contours import get_all_contours
from boilercv_pipeline.stages.find_contours import FindContours


def main(params: FindContours):
    logger.info("Start finding contours")
    destinations = get_unprocessed_destinations(
        params.outs.contours, sources=params.deps.sources, ext="h5"
    )
    for source_name, destination in tqdm(destinations.items()):
        video = bitwise_not(
            scale_bool(
                get_dataset(
                    source_name, sources=params.deps.sources, rois=params.deps.rois
                )[VIDEO].values
            )
        )
        df = get_all_contours(video, method=CHAIN_APPROX_SIMPLE)
        df.to_hdf(destination, key="contours", complib="zlib", complevel=9)
    logger.info("Finish finding contours")


if __name__ == "__main__":
    invoke(FindContours)
