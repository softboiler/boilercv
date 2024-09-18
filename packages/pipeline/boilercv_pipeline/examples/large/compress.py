"""Compress the video data in a NetCDF file.

Compression is slow for grayscale files of ~2GB size, but may work better for binarized
files.
"""

from boilercv.data import VIDEO
from boilercv_pipeline import DEBUG
from boilercv_pipeline.examples.large import example_dataset


@example_dataset(
    destination="compressed", preview=DEBUG, encoding={VIDEO: {"zlib": True}}
)
def main():  # noqa: D103
    pass


if __name__ == "__main__":
    main()
