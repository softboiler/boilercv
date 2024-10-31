"""Convert CINE files to the NetCDF file format."""

from boilercv_pipeline.examples import EXAMPLE_NUM_FRAMES
from boilercv_pipeline.images import prepare_dataset
from boilercv_pipeline.models.paths import paths


def main():  # noqa: D103
    destination = paths.large_examples / f"{paths.large_example_cine.stem}.nc"
    _, ds = prepare_dataset(paths.large_example_cine, num_frames=EXAMPLE_NUM_FRAMES)
    ds.to_netcdf(path=destination)


if __name__ == "__main__":
    main()
