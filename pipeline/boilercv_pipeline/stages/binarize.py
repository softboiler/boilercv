"""Binarize videos and export their ROIs."""

from pathlib import Path
from typing import Any, ClassVar

from cappa.base import command, parse
from loguru import logger
from pydantic import BaseModel, FilePath, ValidationInfo, field_validator
from tqdm import tqdm
from xarray import open_dataset

from boilercv.data import FRAME, ROI, VIDEO, apply_to_img_da
from boilercv.data.packing import pack
from boilercv.images import cv, scale_bool
from boilercv.images.cv import apply_mask, close_and_erode, flood
from boilercv.types import DA
from boilercv_pipeline.contexts import ContextsBaseModel
from boilercv_pipeline.models.config import default, get_kind
from boilercv_pipeline.root_contexts import DataDir, get_config
from boilercv_pipeline.root_contexts.types import RootConfigDict


class MatchedPaths(ContextsBaseModel):
    model_config: ClassVar[RootConfigDict] = get_config()  # pyright: ignore[reportIncompatibleVariableOverride]

    @field_validator("*", mode="before")
    @classmethod
    def validate_paths(cls, value: Any, info: ValidationInfo) -> Any:
        """Model field type matches the default type."""
        if (
            (field_name := info.field_name)
            and (field_info := cls.model_fields.get(field_name))
            and (kind := get_kind(field_info, default.kind_validators))
            and (value not in default.kinds[kind])
        ):
            raise ValueError(
                f"Stage {cls.__name__} has path '{value}' of kind {kind} that doesn't match default paths."
            )
        return value


class Deps(MatchedPaths):
    stage: FilePath = Path(__file__)
    large_sources: DataDir = default.paths.large_sources


class Outs(MatchedPaths):
    sources: DataDir = default.paths.sources
    rois: DataDir = default.paths.rois


@command
class Binarize(BaseModel): ...


def main(_params: Binarize, deps: Deps | None = None, outs: Outs | None = None):
    deps, outs = (deps or Deps(), outs or Outs())
    logger.info("start binarize")
    for source in tqdm(sorted(deps.large_sources.iterdir())):
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
    main(parse(Binarize))
