from loguru import logger
from tqdm import tqdm

from boilercv.data import FRAME, VIDEO
from boilercv_pipeline.parser import invoke
from boilercv_pipeline.preview import new_videos_to_preview
from boilercv_pipeline.sets import get_dataset
from boilercv_pipeline.stages.preview_filled import PreviewFilled


def main(params: PreviewFilled):
    logger.info("Start updating filled preview")
    stage = "filled"
    destination = params.outs.filled_preview
    # TODO: Figure out out-of-order preview frames to avoid reprocessing frames
    with new_videos_to_preview(
        destination, reprocess=True, sources=params.deps.filled
    ) as videos_to_preview:
        for video_name in tqdm(videos_to_preview):
            ds = get_dataset(
                video_name,
                stage=stage,
                num_frames=1,
                sources=params.deps.filled,
                rois=params.deps.rois,
            )
            videos_to_preview[video_name] = ds[VIDEO].isel({FRAME: 0}).values
    logger.info("Finish updating filled preview")


if __name__ == "__main__":
    invoke(PreviewFilled)
