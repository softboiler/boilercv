"""Update previews for the filled contours stage."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from boilercore.models import DefaultPathsModel
from cappa.arg import Arg
from cappa.base import command, invoke
from loguru import logger
from pydantic import BaseModel, Field
from tqdm import tqdm

from boilercv.data import FRAME, VIDEO
from boilercv_pipeline.models import get_parser
from boilercv_pipeline.models.config import default
from boilercv_pipeline.sets import get_dataset
from boilercv_pipeline.stages.common.preview import new_videos_to_preview


class Deps(DefaultPathsModel):
    root: Path = Field(default=default.paths.root, exclude=True)
    stage: Path = Path(__file__)
    sources: Path = default.paths.sources
    filled: Path = default.paths.filled


class Outs(DefaultPathsModel):
    root: Path = Field(default=default.paths.root, exclude=True)
    filled_preview: Path = default.paths.filled_preview


def main(args: PreviewFilled):
    logger.info("Start updating filled preview")
    stage = "filled"
    destination = args.outs.filled_preview
    # TODO: Figure out out-of-order preview frames to avoid reprocessing frames
    with new_videos_to_preview(
        destination,
        names=[source.stem for source in sorted(args.deps.sources.iterdir())],
        reprocess=True,
    ) as videos_to_preview:
        for video_name in tqdm(videos_to_preview):
            ds = get_dataset(video_name, stage=stage, num_frames=1)
            videos_to_preview[video_name] = ds[VIDEO].isel({FRAME: 0}).values
    logger.info("Finish updating filled preview")


@command(invoke=main, default_long=True)
class PreviewFilled(BaseModel):
    deps: Annotated[Deps, Arg(parse=get_parser(Deps), hidden=True)] = Deps()
    outs: Annotated[Outs, Arg(parse=get_parser(Deps), hidden=True)] = Outs()


if __name__ == "__main__":
    invoke(PreviewFilled)
