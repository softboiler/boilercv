"""Unpack the bits of a NetCDF file."""

from boilercv.data import VIDEO
from boilercv.data.packing import unpack
from boilercv_pipeline.examples.large import example_dataset


def main():  # noqa: D103
    with example_dataset(source="packed_compressed", destination="unpacked") as ds:
        ds[VIDEO] = unpack(ds[VIDEO])


if __name__ == "__main__":
    main()
