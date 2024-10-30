import contextlib
from datetime import datetime
from pathlib import Path
from re import match

from loguru import logger
from tomlkit import dumps
from tqdm import tqdm

from boilercv_pipeline.images import prepare_dataset
from boilercv_pipeline.parser import invoke
from boilercv_pipeline.stages.convert import Convert as Params


def main(params: Params):
    logger.info("start convert")
    for source in tqdm(sorted(params.deps.cines.iterdir())):
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
        header, dataset = prepare_dataset(source, crop=matched_crop)
        dataset.to_netcdf(path=destination)
        Path(params.outs.headers / source.name).write_text(
            encoding="utf-8", data=dumps(header.model_dump(mode="json"))
        )
    logger.info("finish convert")


def get_datetime_from_cine(path: Path) -> datetime | None:
    """Get datetime from a cine named by Phantom Cine Viewer's {timeS} scheme."""
    with contextlib.suppress(ValueError):
        return datetime.strptime(path.stem, r"Y%Y%m%dH%H%M%S")
    return None


if __name__ == "__main__":
    invoke(Params)
