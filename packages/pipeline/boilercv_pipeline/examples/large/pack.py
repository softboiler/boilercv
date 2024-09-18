"""Pack the bits of a NetCDF file."""

from boilercv.data import VIDEO
from boilercv.data.packing import pack
from boilercv_pipeline.examples.large import example_dataset


def main():  # noqa: D103
    with example_dataset(source="binarized", destination="packed") as ds:
        ds[VIDEO] = pack(ds[VIDEO])


if __name__ == "__main__":
    main()
