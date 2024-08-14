"""Update previews for the binarization stage."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from boilercore.models import DefaultPathsModel
from cappa.arg import Arg
from cappa.base import command, invoke
from loguru import logger
from pydantic import BaseModel, Field
from tqdm import tqdm

from boilercv.data import FRAME, ROI, VIDEO
from boilercv_pipeline.models.paths import get_parser, paths
from boilercv_pipeline.sets import get_dataset
from boilercv_pipeline.stages.common.preview import new_videos_to_preview


class Deps(DefaultPathsModel):
    root: Path = Field(default=paths.paths.root, exclude=True)
    stage: Path = Path(__file__)
    rois: Path = paths.paths.rois
    sources: Path = paths.paths.sources


class Outs(DefaultPathsModel):
    root: Path = Field(default=paths.paths.root, exclude=True)
    binarized_preview: Path = paths.paths.binarized_preview


def main(args: PreviewBinarized):
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


@command(invoke=main, default_long=True)
class PreviewBinarized(BaseModel):
    deps: Annotated[Deps, Arg(parse=get_parser(Deps), hidden=True)] = Deps()
    outs: Annotated[Outs, Arg(parse=get_parser(Deps), hidden=True)] = Outs()


if __name__ == "__main__":
    invoke(PreviewBinarized)
