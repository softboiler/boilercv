from cappa.base import invoke
from loguru import logger
from tqdm import tqdm

from boilercv.data import FRAME, ROI, VIDEO
from boilercv_pipeline.sets import get_dataset
from boilercv_pipeline.stages.common.preview import new_videos_to_preview
from boilercv_pipeline.stages.preview_binarized import PreviewBinarized


def main(params: PreviewBinarized):
    logger.info("Start updating binarized preview")
    stage = "sources"
    destination = params.outs.binarized_preview
    # TODO: Figure out out-of-order preview frames to avoid reprocessing frames
    with new_videos_to_preview(
        destination, reprocess=True, sources=params.deps.sources
    ) as videos_to_preview:
        for video_name in tqdm(videos_to_preview):
            ds = get_dataset(
                video_name,
                stage=stage,
                num_frames=1,
                sources=params.deps.sources,
                rois=params.deps.rois,
            )
            first_frame = ds[VIDEO].isel({FRAME: 0}).values
            videos_to_preview[video_name] = first_frame & ds[ROI].values
    logger.info("Finish updating binarized preview")


if __name__ == "__main__":
    invoke(PreviewBinarized)
