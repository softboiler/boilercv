"""Fill bubble contours."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from boilercore.models import DefaultPathsModel
from cappa.arg import Arg
from cappa.base import command, invoke
from loguru import logger
from pydantic import BaseModel, Field
from tqdm import tqdm
from xarray import zeros_like

from boilercv.data import ROI, VIDEO
from boilercv.data.packing import pack
from boilercv.images import scale_bool
from boilercv.images.cv import draw_contours
from boilercv.types import ArrInt
from boilercv_pipeline.models import get_parser
from boilercv_pipeline.models.config import default
from boilercv_pipeline.sets import get_contours_df, get_dataset, process_datasets


class Deps(DefaultPathsModel):
    root: Path = Field(default=default.paths.root, exclude=True)
    stage: Path = Path(__file__)
    sources: Path = default.paths.sources
    contours: Path = default.paths.contours


class Outs(DefaultPathsModel):
    root: Path = Field(default=default.paths.root, exclude=True)
    filled: Path = default.paths.filled


def main(args: Fill):
    logger.info("Start filling contours")
    destination = args.outs.filled
    with process_datasets(
        destination,
        names=[source.stem for source in sorted(args.deps.sources.iterdir())],
    ) as videos_to_process:
        for name in tqdm(videos_to_process):
            df = get_contours_df(name)
            source_ds = get_dataset(name)
            ds = zeros_like(source_ds, dtype=source_ds[VIDEO].dtype)
            video = ds[VIDEO]
            if not df.empty:
                for frame_num, frame in enumerate(video):
                    contours: list[ArrInt] = list(  # pyright: ignore[reportAssignmentType]
                        df.loc[frame_num, :]
                        .groupby("contour")
                        .apply(lambda grp: grp.values)
                    )
                    video[frame_num, :, :] = draw_contours(
                        scale_bool(frame.values), contours
                    )
            ds[VIDEO] = pack(video)
            ds = ds.drop_vars(ROI)
            videos_to_process[name] = ds
    logger.info("Finish filling contours")


@command(invoke=main, default_long=True)
class Fill(BaseModel):
    deps: Annotated[Deps, Arg(parse=get_parser(Deps), hidden=True)] = Deps()
    outs: Annotated[Outs, Arg(parse=get_parser(Deps), hidden=True)] = Outs()


if __name__ == "__main__":
    invoke(Fill)
