"""Datasets."""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from pandas import read_hdf
from xarray import Dataset, open_dataset

from boilercv.correlations.types import Stage
from boilercv.data import FRAME, HEADER, ROI, VIDEO, XPX, YPX
from boilercv.data.packing import unpack
from boilercv.types import DF, DS
from boilercv_pipeline.models.paths import Paths
from boilercv_pipeline.models.stages import ROOTED
from boilercv_pipeline.models.types.runtime import get_boilercv_pipeline_context

ROOTED_PATHS = Paths(_context=get_boilercv_pipeline_context(ROOTED))
"""Paths rooted to their directories."""
ALL_FRAMES = slice(None)
"""Slice that gets all frames."""
STAGE_DEFAULT = "sources"
"""Default stage to work on."""


@contextmanager
def process_datasets(
    destination_dir: Path, reprocess: bool = False, sources: Path = ROOTED_PATHS.sources
) -> Iterator[dict[str, Any]]:
    """Get unprocessed dataset names and write them to disk.

    Use as a context manager. Given a destination directory, yield a mapping with
    unprocessed dataset names as its keys. Upon exiting the context, datasets assigned
    to the values of the mapping will be written to disk in the destination directory.

    If no values are assigned to the yielded mapping, no datasets will be written. This
    is useful for processes which take input datasets but handle their own output,
    perhaps to a different file format.

    Args:
        destination_dir: The directory to write datasets to.
        reprocess: Whether to reprocess all datasets.
    """
    unprocessed_destinations = get_unprocessed_destinations(
        destination_dir, sources=sources, reprocess=reprocess
    )
    datasets_to_process = dict.fromkeys(unprocessed_destinations)
    yield datasets_to_process
    for name, ds in datasets_to_process.items():
        if ds is None:
            continue
        ds.to_netcdf(
            path=unprocessed_destinations[name], encoding={VIDEO: {"zlib": True}}
        )


def get_unprocessed_destinations(
    destination_dir: Path,
    ext: str = "nc",
    reprocess: bool = False,
    sources: Path = ROOTED_PATHS.sources,
) -> dict[str, Path]:
    """Get destination paths for unprocessed datasets.

    Given a destination directory, yield a mapping of unprocessed dataset names to
    destinations with a given file extension. A dataset is considered unprocessed if a
    file sharing its name is not found in the destination directory.

    Parameters
    ----------
    names
        Names of the datasets to process.
    destination_dir
        Desired destination directory.
    ext
        Desired file extension.
    reprocess
        Reprocess all datasets.
    sources
        Directory of sources to be processed.

    Returns
    -------
    A mapping of unprocessed dataset names to destinations with the given file.
    """
    unprocessed_destinations: dict[str, Path] = {}
    ext = ext.lstrip(".")
    for name in [source.stem for source in sorted(sources.iterdir())]:
        destination = destination_dir / f"{name}.{ext}"
        if reprocess or not destination.exists():
            unprocessed_destinations[name] = destination
    return unprocessed_destinations


def inspect_dataset(
    name: str, stage: Stage = STAGE_DEFAULT, sources: Path = ROOTED_PATHS.sources
) -> DS:
    """Inspect a video dataset."""
    cmp_source, unc_source = get_stage(name, sources)
    source = unc_source if unc_source.exists() else cmp_source
    if stage == "large_sources":
        return open_dataset(source) if source.exists() else Dataset()
    with open_dataset(source) as ds:
        return ds


def get_dataset(
    name: str,
    num_frames: int = 0,
    frame: slice = ALL_FRAMES,
    stage: Stage = STAGE_DEFAULT,
    sources: Path = ROOTED_PATHS.sources,
    rois: Path = ROOTED_PATHS.rois,
) -> DS:
    """Load a video dataset."""
    # Can't use `xarray.open_mfdataset` because it requires dask
    # Unpacking is incompatible with dask
    frame = slice_frames(num_frames, frame)
    cmp_source, unc_source = get_stage(name, sources)
    source = unc_source if unc_source.exists() else cmp_source
    if stage == "large_sources":
        ds = open_dataset(source)
        return (
            Dataset({VIDEO: ds[VIDEO].sel(frame=frame), HEADER: ds[HEADER]})
            if source.exists()
            else Dataset()
        )
    roi = rois / f"{name}.nc"
    with open_dataset(source) as ds, open_dataset(roi) as roi_ds:
        if not unc_source.exists():
            Dataset({VIDEO: ds[VIDEO], HEADER: ds[HEADER]}).to_netcdf(
                path=unc_source, encoding={VIDEO: {"zlib": False}}
            )
        return Dataset({
            VIDEO: unpack(ds[VIDEO].sel(frame=frame)),
            ROI: roi_ds[ROI],
            HEADER: ds[HEADER],
        })


def get_dataset2(path: Path, slices: dict[str, slice] | None = None) -> DS:
    """Load a video dataset."""
    # Can't use `xarray.open_mfdataset` because it requires dask
    # Unpacking is incompatible with dask
    slices = slices or {}
    cmp_source, unc_source = get_stage(path.stem, path.parent)
    source = unc_source if unc_source.exists() else cmp_source
    video = open_dataset(source)[VIDEO]
    if not unc_source.exists():
        Dataset({VIDEO: video}).to_netcdf(
            path=unc_source, encoding={VIDEO: {"zlib": False}}
        )
    return Dataset({
        VIDEO: unpack(
            video.sel({
                FRAME: slices.get("frame", slice(None)),
                YPX: slices.get(YPX, slice(None)),
            })
        ).sel({XPX: slices.get(XPX, slice(None))})
    })


def get_stage(name: str, sources: Path) -> tuple[Path, Path]:
    """Get the paths associated with a particular video name and pipeline stage."""
    source = sources / f"{name}.nc"
    (uncompressed := sources.with_name(f"uncompressed_{sources.name}")).mkdir(
        parents=True, exist_ok=True
    )
    return source, uncompressed / f"{name}.nc"


def get_contours_df(name: str, contours: Path = ROOTED_PATHS.contours) -> DF:
    """Load contours from a dataset."""
    (
        uncompressed_contours := contours.with_name(f"uncompressed_{contours.name}")
    ).mkdir(parents=True, exist_ok=True)
    unc_cont = uncompressed_contours / f"{name}.h5"
    contour = unc_cont if unc_cont.exists() else contours / f"{name}.h5"
    contour_df: DF = read_hdf(contour)  # pyright: ignore[reportAssignmentType]
    if not unc_cont.exists():
        contour_df.to_hdf(unc_cont, key="contours", complevel=None, complib=None)
    return contour_df


def slice_frames(num_frames: int = 0, frame: slice = ALL_FRAMES) -> slice:
    """Return a slice suitable for getting frames from datasets."""
    if num_frames:
        if frame == ALL_FRAMES:
            frame = slice(None, num_frames - 1)
        else:
            raise ValueError("Don't specify both `num_frames` and `frame`.")
    return frame
