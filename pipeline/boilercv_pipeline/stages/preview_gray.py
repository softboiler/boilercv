"""Update previews for grayscale videos."""

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


class Params(BaseModel):
    """Stage parameters."""


class Deps(DefaultPathsModel):
    """Stage dependencies."""

    root: Path = Field(default=default.paths.root, exclude=True)
    sources: Path = default.paths.sources


class Outs(DefaultPathsModel):
    """Stage outputs."""

    root: Path = Field(default=default.paths.root, exclude=True)
    gray_preview: Path = default.paths.gray_preview


def main(args: PreviewGray):
    logger.info("Start updating gray preview")
    stage = "large_sources"
    destination = args.outs.gray_preview
    with new_videos_to_preview(
        destination,
        names=[source.stem for source in sorted(args.deps.sources.iterdir())],
        reprocess=True,
    ) as videos_to_preview:
        for video_name in tqdm(videos_to_preview):
            if ds := get_dataset(video_name, stage=stage, num_frames=1):
                videos_to_preview[video_name] = ds[VIDEO].isel({FRAME: 0}).values
    logger.info("Finish updating gray preview")


@command(invoke=main, default_long=True)
class PreviewGray(BaseModel):
    params: Annotated[Params, Arg(parse=get_parser(Params))] = Params()
    deps: Annotated[Deps, Arg(parse=get_parser(Deps))] = Deps()
    outs: Annotated[Outs, Arg(parse=get_parser(Outs))] = Outs()


if __name__ == "__main__":
    invoke(PreviewGray)
