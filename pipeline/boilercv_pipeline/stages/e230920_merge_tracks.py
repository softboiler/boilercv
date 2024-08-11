"""Merge tracks."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from boilercore.models import DefaultPathsModel
from cappa.arg import Arg
from cappa.base import command, invoke
from pandas import concat, read_hdf
from pydantic import BaseModel, Field

from boilercv_pipeline.models import get_parser
from boilercv_pipeline.models.config import default
from boilercv_pipeline.stages.common.e230920 import get_e230920_times


class Params(BaseModel):
    """Stage parameters."""


class Deps(DefaultPathsModel):
    """Stage dependencies."""

    root: Path = Field(default=default.paths.root, exclude=True)
    e230920_processed_tracks: Path = default.paths.e230920_processed_tracks


class Outs(DefaultPathsModel):
    """Stage outputs."""

    root: Path = Field(default=default.paths.root, exclude=True)
    e230920_merged_tracks: Path = default.paths.e230920_merged_tracks


def main(args: E230920MergeTracks):
    concat([
        read_hdf(
            (
                args.deps.e230920_processed_tracks
                / f"processed_tracks_{time.replace(':', '-')}"
            ).with_suffix(".h5")
        ).assign(**{"datetime": time})
        for time in get_e230920_times(args.deps.e230920_processed_tracks)
    ]).to_hdf(
        args.outs.e230920_merged_tracks, key="tracks", complib="zlib", complevel=9
    )


@command(invoke=main, default_long=True)
class E230920MergeTracks(BaseModel):
    params: Annotated[Params, Arg(parse=get_parser(Params))] = Params()
    deps: Annotated[Deps, Arg(parse=get_parser(Deps))] = Deps()
    outs: Annotated[Outs, Arg(parse=get_parser(Outs))] = Outs()


if __name__ == "__main__":
    invoke(E230920MergeTracks)
