"""Convert CINE files to the NetCDF file format."""

from boilercv_pipeline.examples import EXAMPLE_NUM_FRAMES
from boilercv_pipeline.models.config import default
from boilercv_pipeline.video import prepare_dataset


def main():  # noqa: D103
    destination = (
        default.params.paths.large_examples
        / f"{default.params.paths.large_example_cine.stem}.nc"
    )
    ds = prepare_dataset(
        default.params.paths.large_example_cine, num_frames=EXAMPLE_NUM_FRAMES
    )
    ds.to_netcdf(path=destination)


if __name__ == "__main__":
    main()
