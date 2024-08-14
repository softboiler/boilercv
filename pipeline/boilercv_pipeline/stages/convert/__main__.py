"""Convert all CINEs to NetCDF."""

from __future__ import annotations

import contextlib
from datetime import datetime
from pathlib import Path
from re import match

from cappa.base import invoke
from loguru import logger
from tqdm import tqdm

from boilercv_pipeline.stages.convert import Convert
from boilercv_pipeline.video import prepare_dataset


def main(params: Convert):
    logger.info("start convert")
    for source in tqdm(sorted(params.deps.cines.iterdir())):
        continue
        if dt := get_datetime_from_cine(source):
            destination_stem = dt.isoformat().replace(":", "-")
        else:
            destination_stem = source.stem
        destination = params.outs.large_sources / f"{destination_stem}.nc"
        if destination.exists():
            continue
        matched_crop = None
        for pattern, crop in {}.items():  # TODO: Reimplement crop property
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
    invoke(Convert)
