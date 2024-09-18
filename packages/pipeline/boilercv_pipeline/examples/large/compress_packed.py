"""Compress the packed video data in a NetCDF file.

This is much quicker, and yields another 8x compresssion ratio on top of the packing.
"""

from boilercv.data import VIDEO
from boilercv_pipeline import DEBUG
from boilercv_pipeline.examples.large import example_dataset


@example_dataset(
    source="packed",
    destination="packed_compressed",
    preview=DEBUG,
    encoding={VIDEO: {"zlib": True}},
)
def main():  # noqa: D103
    pass


if __name__ == "__main__":
    main()
