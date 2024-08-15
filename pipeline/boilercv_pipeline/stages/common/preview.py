"""Update previews for various stages."""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from xarray import combine_by_coords, open_dataset

from boilercv.data import VIDEO, VIDEO_NAME, XPX, YPX, assign_ds
from boilercv.data.models import Dimension
from boilercv.types import DS
from boilercv_pipeline.captivate.previews import pad_images
from boilercv_pipeline.models.paths import paths


@contextmanager
def new_videos_to_preview(
    destination: Path, reprocess: bool = False, sources: Path = paths.sources
) -> Iterator[dict[str, Any]]:
    """Get empty mapping of new videos to preview and write to disk."""
    # Yield a mapping of new video names to previews, to be populated by the user
    names = [source.stem for source in sorted(sources.iterdir())]
    if reprocess:
        # Reprocess all names
        new_video_names = names
    else:
        # Get the names missing from the destination
        existing_names: list[str] = []
        if destination.exists():
            with open_dataset(destination) as existing_ds:
                existing_names.extend(list(existing_ds[VIDEO_NAME].values))
        new_video_names = [name for name in names if name not in existing_names]
    videos_to_preview = dict.fromkeys(new_video_names)

    yield videos_to_preview

    # Keep only valid received previews and build a dataset of new previews
    if received_previews := {
        video_name: preview
        for video_name, preview in videos_to_preview.items()
        if preview is not None and video_name in new_video_names
    }:
        received_video_names = list(received_previews.keys())
        received_previews = list(received_previews.values())
        new_ds = get_preview_ds(received_video_names, received_previews)

        if not reprocess and destination.exists():
            with open_dataset(destination) as existing_ds:
                if new_ds[VIDEO].shape == existing_ds[VIDEO].shape:
                    # Combine datasets if they're the same shape
                    new_ds = combine_by_coords([existing_ds, new_ds])
                else:
                    # Otherwise: destructure, pad, and rebuild them together
                    existing_names = list(existing_ds[VIDEO_NAME].values)
                    new_ds = get_preview_ds(
                        existing_names + received_video_names,
                        received_previews + list(existing_ds.video.values),
                    )

        new_ds.to_netcdf(path=destination, encoding={VIDEO: {"zlib": True}})


def get_preview_ds(preview_names: list[str], previews: list[Any]) -> DS:
    """Get a dataset of preview images, padding sizes as necessary."""
    return assign_ds(
        name=VIDEO,
        long_name="Video preview",
        units="Pixel state",
        data=pad_images(previews),
        dims=(
            Dimension(dim=VIDEO_NAME, long_name="Video name", coords=preview_names),
            Dimension(dim=YPX, long_name="Height", units="px"),
            Dimension(dim=XPX, long_name="Width", units="px"),
        ),
    )
