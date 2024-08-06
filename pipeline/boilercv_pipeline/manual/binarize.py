"""Binarize all videos and export their ROIs."""

from loguru import logger
from tqdm import tqdm
from xarray import open_dataset

from boilercv.data import FRAME, ROI, VIDEO, apply_to_img_da
from boilercv.data.packing import pack
from boilercv.images import scale_bool
from boilercv.images.cv import apply_mask, binarize, close_and_erode, flood
from boilercv.types import DA
from boilercv_pipeline.config import default
from boilercv_pipeline.models import Params
from boilercv_pipeline.models.paths import get_sorted_paths


def main(params: Params | None = None):  # noqa: D103
    params = params or default.params
    logger.info("start binarize")
    for source in tqdm(get_sorted_paths(params.paths.large_sources)):
        destination = params.paths.sources / f"{source.stem}.nc"
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
            binarized: DA = apply_to_img_da(binarize, masked, vectorize=True)
            ds[VIDEO] = pack(binarized)
            ds.to_netcdf(
                path=params.paths.sources / source.name,
                encoding={VIDEO: {"zlib": True}},
            )
            ds[ROI] = roi
            ds = ds.drop_vars(VIDEO)
            ds.to_netcdf(path=params.paths.rois / source.name)
    logger.info("finish binarize")


if __name__ == "__main__":
    main()
