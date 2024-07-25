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
    """Paths associated with project requirements and code."""

    # * Roots
    project: DirectoryPath = PROJECT_PATH
    data: DirectoryPath = project / "data"

    # * Local inputs
    cines: DirectoryPath = data / "cines"
    hierarchical_data: DirectoryPath = data / "hierarchical_data"
    large_examples: DirectoryPath = data / "large_examples"
    large_sources: DirectoryPath = data / "large_sources"
    notes: DirectoryPath = data / "notes"
    profiles: DirectoryPath = data / "profiles"
    sheets: DirectoryPath = data / "sheets"
    # ! Uncompressed data
    uncompressed_contours: DirectoryPath = data / "uncompressed_contours"
    uncompressed_filled: DirectoryPath = data / "uncompressed_filled"
    uncompressed_sources: DirectoryPath = data / "uncompressed_sources"
    # ! Examples
    example_cines: DirectoryPath = data / "example_cines"
    large_example_cine: Path = example_cines / "2022-01-06T16-57-31.cine"

    # * Local results
    docx: DirectoryPath = data / "docx"
    html: DirectoryPath = data / "html"
    md: DirectoryPath = data / "md"
    media: DirectoryPath = data / "media"

    # * Git-tracked inputs
    # ! Package
    package: DirectoryPath = get_package_dir(boilercv_pipeline)
    models: DirectoryPath = package / "models"
    paths_module: FilePath = models / "paths.py"
    stages: dict[str, FilePath] = map_stages(package / "stages")
    # ! Plotting config
    plot_config: DirectoryPath = data / "plotting"
    mpl_base: FilePath = plot_config / "base.mplstyle"
    mpl_hide_title: FilePath = plot_config / "hide_title.mplstyle"

    # * DVC-tracked inputs
    experiments: DirectoryPath = data / "experiments"
    notebooks: DirectoryPath = data / "notebooks"
    rois: DirectoryPath = data / "rois"
    samples: DirectoryPath = data / "samples"
    sources: DirectoryPath = data / "sources"

    # * DVC-tracked results
    contours: DirectoryPath = data / "contours"
    examples: DirectoryPath = data / "examples"
    filled: DirectoryPath = data / "filled"
    lifetimes: DirectoryPath = data / "lifetimes"
    tracks: DirectoryPath = data / "tracks"
    unobstructed: DirectoryPath = data / "unobstructed"
    # ! Previews
    previews: DirectoryPath = data / "previews"
    binarized_preview: Path = previews / "binarized.nc"
    filled_preview: Path = previews / "filled.nc"
    gray_preview: Path = previews / "gray.nc"
