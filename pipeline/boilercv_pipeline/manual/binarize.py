"""Binarize videos and export their ROIs."""

from pathlib import Path

from boilercore.models import CreatePathsModel
from loguru import logger
from pydantic import DirectoryPath
from tqdm import tqdm
from xarray import open_dataset

from boilercv.data import FRAME, ROI, VIDEO, apply_to_img_da
from boilercv.data.packing import pack
from boilercv.images import cv, scale_bool
from boilercv.images.cv import apply_mask, close_and_erode, flood
from boilercv.types import DA
from boilercv_pipeline.models import Params
from boilercv_pipeline.models.config import default
from boilercv_pipeline.models.paths import get_sorted_paths


class Deps(CreatePathsModel):  # noqa: D101
    root: Path = default.params.paths.root
    large_sources: DirectoryPath = default.params.paths.large_sources


class Outs(CreatePathsModel):  # noqa: D101
    root: Path = default.params.paths.root
    sources: DirectoryPath = default.params.paths.sources
    rois: DirectoryPath = default.params.paths.rois


def main(_params: Params, deps: Deps, outs: Outs):  # noqa: D103
    logger.info("start binarize")
    deps, outs = Deps(), Outs()
    for source in tqdm(get_sorted_paths(deps.large_sources)):
        destination = outs.sources / f"{source.stem}.nc"
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
                path=outs.sources / source.name, encoding={VIDEO: {"zlib": True}}
            )
            ds[ROI] = roi
            ds = ds.drop_vars(VIDEO)
            ds.to_netcdf(path=outs.rois / source.name)
    logger.info("finish binarize")


if __name__ == "__main__":
    main(default.params, Deps(), Outs())
