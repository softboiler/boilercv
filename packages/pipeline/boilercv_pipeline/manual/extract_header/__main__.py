from pathlib import Path

from boilercv_pipeline.manual.extract_header import ExtractHeader as Params
from boilercv_pipeline.models.header import CineHeader
from boilercv_pipeline.parser import invoke
from boilercv_pipeline.sets import load_video
from loguru import logger
from tomlkit import dumps
from tqdm import tqdm
from xarray import Dataset, open_dataset

from boilercv.data import VIDEO
from boilercv.data.packing import pack


def main(params: Params):
    logger.info("start header extraction")
    for source in tqdm(sorted(params.deps.sources.iterdir())):
        destination = params.outs.headers / source.name
        if destination.exists():
            continue
        with open_dataset(source) as ds:
            Path(f"{params.outs.headers / source.stem}.toml").write_text(
                encoding="utf-8",
                data=dumps(CineHeader(**ds.header.attrs).model_dump(mode="json")),
            )
        with load_video(source) as video:
            Dataset({VIDEO: pack(video)}).to_netcdf(
                path=source, encoding={VIDEO: {"zlib": True}}
            )
    logger.info("finish header extraction")


if __name__ == "__main__":
    invoke(Params)
