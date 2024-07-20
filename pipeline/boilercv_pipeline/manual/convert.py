"""Convert all CINEs to NetCDF."""

import contextlib
from datetime import datetime
from pathlib import Path
from re import match

from loguru import logger
from tqdm import tqdm

from boilercv_pipeline.models.params import PARAMS
from boilercv_pipeline.models.paths import get_sorted_paths
from boilercv_pipeline.video import prepare_dataset


def main():  # noqa: D103
    logger.info("start convert")
    for source in tqdm(get_sorted_paths(PARAMS.paths.cines)):
        if dt := get_datetime_from_cine(source):
            destination_stem = dt.isoformat().replace(":", "-")
        else:
            destination_stem = source.stem
        destination = PARAMS.paths.large_sources / f"{destination_stem}.nc"
        if destination.exists():
            continue
        matched_crop = None
        for pattern, crop in PARAMS.cine_crops.items():
            if match(pattern, source.stem):
                matched_crop = crop
        dataset = prepare_dataset(source, crop=matched_crop)
        dataset.to_netcdf(path=destination)
    logger.info("finish convert")


def get_datetime_from_cine(path: Path) -> datetime | None:
    """Get datetime from a cine named by Phantom Cine Viewer's {timeS} scheme."""
    with contextlib.suppress(ValueError):
        return datetime.strptime(path.stem, r"Y%Y%m%dH%H%M%S")
    return None


if __name__ == "__main__":
    main()
