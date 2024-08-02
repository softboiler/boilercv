"""Project paths."""

from pathlib import Path

from boilercore.models import CreatePathsModel
from boilercore.paths import get_package_dir, map_stages
from pydantic import DirectoryPath, FilePath

import boilercv_pipeline
from boilercv_pipeline import PROJECT_PATH


def get_sorted_paths(path: Path) -> list[Path]:
    """Iterate over a sorted directory."""
    return sorted(path.iterdir())


class Paths(CreatePathsModel):
    """Paths relevant to the project."""

    # * Roots
    root: DirectoryPath = PROJECT_PATH / "data"

    # * Local inputs
    cines: DirectoryPath = root / "cines"
    hierarchical_data: DirectoryPath = root / "hierarchical_data"
    large_examples: DirectoryPath = root / "large_examples"
    large_sources: DirectoryPath = root / "large_sources"
    notes: DirectoryPath = root / "notes"
    profiles: DirectoryPath = root / "profiles"
    sheets: DirectoryPath = root / "sheets"
    # ! Uncompressed data
    uncompressed_contours: DirectoryPath = root / "uncompressed_contours"
    uncompressed_filled: DirectoryPath = root / "uncompressed_filled"
    uncompressed_sources: DirectoryPath = root / "uncompressed_sources"
    # ! Examples
    example_cines: DirectoryPath = root / "example_cines"
    large_example_cine: Path = example_cines / "2022-01-06T16-57-31.cine"

    # * Local results
    docx: DirectoryPath = root / "docx"
    html: DirectoryPath = root / "html"
    md: DirectoryPath = root / "md"
    media: DirectoryPath = root / "media"

    # * Git-tracked inputs
    # ! Plotting config
    plot_config: DirectoryPath = root / "plotting"
    mpl_base: FilePath = plot_config / "base.mplstyle"
    mpl_hide_title: FilePath = plot_config / "hide_title.mplstyle"

    # * DVC_tracked imports
    modelfunctions: Path = root / "models"

    # * DVC-tracked inputs
    experiments: DirectoryPath = root / "experiments"
    notebooks: DirectoryPath = root / "notebooks"
    rois: DirectoryPath = root / "rois"
    samples: DirectoryPath = root / "samples"
    sources: DirectoryPath = root / "sources"

    # * DVC-tracked results
    contours: DirectoryPath = root / "contours"
    examples: DirectoryPath = root / "examples"
    filled: DirectoryPath = root / "filled"
    lifetimes: DirectoryPath = root / "lifetimes"
    tracks: DirectoryPath = root / "tracks"
    unobstructed: DirectoryPath = root / "unobstructed"
    # ! Previews
    previews: DirectoryPath = root / "previews"
    binarized_preview: Path = previews / "binarized.nc"
    filled_preview: Path = previews / "filled.nc"
    gray_preview: Path = previews / "gray.nc"


class PackagePaths(CreatePathsModel):
    """Package paths."""

    # * Git-tracked inputs
    # ! Package
    root: DirectoryPath = get_package_dir(boilercv_pipeline)
    models: DirectoryPath = root / "models"
    paths_module: FilePath = models / "paths.py"
    stages: dict[str, FilePath] = map_stages(root / "stages")
