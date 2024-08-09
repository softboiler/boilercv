"""Update previews for the binarization stage."""

from cappa.base import invoke
from loguru import logger
from tqdm import tqdm

from boilercv.data import FRAME, ROI, VIDEO
from boilercv_pipeline import defaults_backend
from boilercv_pipeline.models.generated.stages.preview_binarized import PreviewBinarized
from boilercv_pipeline.sets import get_dataset
from boilercv_pipeline.stages.common.preview import new_videos_to_preview


def main(args: PreviewBinarized):  # noqa: D103
    logger.info("Start updating binarized preview")
    stage = "sources"
    destination = args.outs.binarized_preview
    # TODO: Figure out out-of-order preview frames to avoid reprocessing frames
    with new_videos_to_preview(
        destination,
        names=[source.stem for source in sorted(args.deps.sources.iterdir())],
        reprocess=True,
    ) as videos_to_preview:
        for video_name in tqdm(videos_to_preview):
            ds = get_dataset(video_name, stage=stage, num_frames=1)
            first_frame = ds[VIDEO].isel({FRAME: 0}).values
            videos_to_preview[video_name] = first_frame & ds[ROI].values
    logger.info("Finish updating binarized preview")


if __name__ == "__main__":
    invoke(PreviewBinarized, backend=defaults_backend)
