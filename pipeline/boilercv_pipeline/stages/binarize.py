"""Binarize videos and export their ROIs."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from boilercore.models import DefaultPathsModel
from cappa.arg import Arg
from cappa.base import command, invoke
from loguru import logger
from pydantic import BaseModel, Field
from tqdm import tqdm
from xarray import open_dataset

from boilercv.data import FRAME, ROI, VIDEO, apply_to_img_da
from boilercv.data.packing import pack
from boilercv.images import cv, scale_bool
from boilercv.images.cv import apply_mask, close_and_erode, flood
from boilercv.types import DA
from boilercv_pipeline.models import get_parser
from boilercv_pipeline.models.config import default


class Deps(DefaultPathsModel):
    root: Path = Field(default=default.paths.root, exclude=True)
    large_sources: Path = default.paths.large_sources


class Outs(DefaultPathsModel):
    root: Path = Field(default=default.paths.root, exclude=True)
    sources: Path = default.paths.sources
    rois: Path = default.paths.rois


def main(args: Binarize):
    logger.info("start binarize")
    for source in tqdm(sorted(args.deps.large_sources.iterdir())):
        destination = args.outs.sources / f"{source.stem}.nc"
        if destination.exists():
            continue
        with open_dataset(source) as ds:
            video = ds[VIDEO]
            maximum = video.max(FRAME)
            flooded: DA = apply_to_img_da(flood, maximum)
            roi: DA = apply_to_img_da(close_and_erode, scale_bool(flooded))
            masked: DA = apply_to_img_da(
                apply_mask, video, scale_bool(roi), vectorize=True
            )
            binarized: DA = apply_to_img_da(cv.binarize, masked, vectorize=True)
            ds[VIDEO] = pack(binarized)
            ds.to_netcdf(
                path=args.outs.sources / source.name, encoding={VIDEO: {"zlib": True}}
            )
            ds[ROI] = roi
            ds = ds.drop_vars(VIDEO)
            ds.to_netcdf(path=args.outs.rois / source.name)
    logger.info("finish binarize")


@command(invoke=main, default_long=True)
class Binarize(BaseModel):
    deps: Annotated[Deps, Arg(parse=get_parser(Deps), hidden=True)] = Deps()
    outs: Annotated[Outs, Arg(parse=get_parser(Deps), hidden=True)] = Outs()


if __name__ == "__main__":
    invoke(Binarize)
