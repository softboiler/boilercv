"""Convert all CINEs to NetCDF."""

from __future__ import annotations

import contextlib
from datetime import datetime
from pathlib import Path
from re import match
from typing import Annotated

from boilercore.models import DefaultPathsModel
from cappa.arg import Arg
from cappa.base import command, invoke
from loguru import logger
from pydantic import BaseModel, Field
from tqdm import tqdm

from boilercv_pipeline.models import get_parser
from boilercv_pipeline.models.config import default
from boilercv_pipeline.video import prepare_dataset


class Deps(DefaultPathsModel):
    root: Path = Field(default=default.paths.root, exclude=True)
    cines: Path = default.paths.cines


class Outs(DefaultPathsModel):
    root: Path = Field(default=default.paths.root, exclude=True)
    large_sources: Path = default.paths.large_sources


def main(args: Convert):
    logger.info("start convert")
    for source in tqdm(sorted(args.deps.cines.iterdir())):
        if dt := get_datetime_from_cine(source):
            destination_stem = dt.isoformat().replace(":", "-")
        else:
            destination_stem = source.stem
        destination = args.outs.large_sources / f"{destination_stem}.nc"
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


@command(invoke=main, default_long=True)
class Convert(BaseModel):
    deps: Annotated[Deps, Arg(parse=get_parser(Deps), hidden=True)] = Deps()
    outs: Annotated[Outs, Arg(parse=get_parser(Deps), hidden=True)] = Outs()


if __name__ == "__main__":
    invoke(Convert)
