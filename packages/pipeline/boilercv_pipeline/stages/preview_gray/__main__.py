from loguru import logger
from tqdm import tqdm

from boilercv.data import FRAME, VIDEO
from boilercv_pipeline.parser import invoke
from boilercv_pipeline.preview import new_videos_to_preview
from boilercv_pipeline.sets import get_dataset
from boilercv_pipeline.stages.preview_gray import PreviewGray


def main(params: PreviewGray):
    logger.info("Start updating gray preview")
    stage = "large_sources"
    destination = params.outs.gray_preview
    with new_videos_to_preview(
        destination, reprocess=True, sources=params.deps.large_sources
    ) as videos_to_preview:
        for video_name in tqdm(videos_to_preview):
            if ds := get_dataset(
                video_name, stage=stage, num_frames=1, sources=params.deps.large_sources
            ):
                videos_to_preview[video_name] = ds[VIDEO].isel({FRAME: 0}).values
    logger.info("Finish updating gray preview")


if __name__ == "__main__":
    invoke(PreviewGray)
