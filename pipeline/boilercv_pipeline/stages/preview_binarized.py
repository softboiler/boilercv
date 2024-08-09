"""Update previews for the binarization stage."""

from loguru import logger
from tqdm import tqdm

from boilercv.data import FRAME, ROI, VIDEO
from boilercv_pipeline.config import default
from boilercv_pipeline.sets import get_dataset
from boilercv_pipeline.stages.common.preview import new_videos_to_preview


def main():  # noqa: D103
    stage = "sources"
    destination = default.params.paths.binarized_preview
    # TODO: Figure out out-of-order preview frames to avoid reprocessing frames
    with new_videos_to_preview(destination, reprocess=True) as videos_to_preview:
        for video_name in tqdm(videos_to_preview):
            ds = get_dataset(video_name, stage=stage, num_frames=1)
            first_frame = ds[VIDEO].isel({FRAME: 0}).values
            videos_to_preview[video_name] = first_frame & ds[ROI].values


if __name__ == "__main__":
    logger.info("Start updating binarized preview")
    main()
    logger.info("Finish updating binarized preview")
