"""Merge tracks."""

from pandas import concat, read_hdf

from boilercv_pipeline.stages.common.e230920 import (
    EXP_TIMES,
    MERGED_TRACKS,
    PROCESSED_TRACKS,
)


def main():  # noqa: D103
    concat([
        read_hdf(
            (
                PROCESSED_TRACKS
                / f"processed_tracks_{time.isoformat().replace(':', '-')}"
            ).with_suffix(".h5")
        ).assign(**{"datetime": time.isoformat()})
        for time in EXP_TIMES
    ]).to_hdf(MERGED_TRACKS, key="tracks", complib="zlib", complevel=9)


if __name__ == "__main__":
    main()
