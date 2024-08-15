"""Merge tracks."""

from __future__ import annotations

from cappa.base import invoke
from pandas import concat, read_hdf

from boilercv_pipeline.stages.common.e230920 import get_e230920_times
from boilercv_pipeline.stages.e230920_merge_tracks import E230920MergeTracks


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


if __name__ == "__main__":
    invoke(E230920MergeTracks)
