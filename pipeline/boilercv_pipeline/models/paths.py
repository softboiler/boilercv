"""Project paths."""

from pathlib import Path
from shlex import quote
from subprocess import run
from textwrap import dedent
from typing import Any, get_args

from boilercore.models import DefaultPathsModel
from boilercore.paths import get_package_dir, map_stages
from pydantic import DirectoryPath, FilePath, model_validator

import boilercv_pipeline
from boilercv_pipeline.models.types.generated.stages import ManualStageName, StageName


def get_sorted_paths(path: Path) -> list[Path]:
    """Iterate over a sorted directory."""
    return sorted(path.iterdir())


class Paths(DefaultPathsModel):
    """Paths relevant to the project."""

    # * Roots
    root: Path = Path.cwd() / "data"

    # * Local inputs
    cines: Path = root / "cines"
    hierarchical_data: Path = root / "hierarchical_data"
    large_examples: Path = root / "large_examples"
    large_sources: Path = root / "large_sources"
    notes: Path = root / "notes"
    profiles: Path = root / "profiles"
    sheets: Path = root / "sheets"
    # ! Uncompressed data
    uncompressed_contours: Path = root / "uncompressed_contours"
    uncompressed_filled: Path = root / "uncompressed_filled"
    uncompressed_sources: Path = root / "uncompressed_sources"
    # ! Examples
    example_cines: Path = root / "example_cines"
    large_example_cine: Path = example_cines / "2022-01-06T16-57-31.cine"

    # * Local results
    docx: Path = root / "docx"
    html: Path = root / "html"
    md: Path = root / "md"
    media: Path = root / "media"

    # * Git-tracked inputs
    # ! Plotting config
    plot_config: Path = root / "plotting"
    mpl_base: Path = plot_config / "base.mplstyle"
    mpl_hide_title: Path = plot_config / "hide_title.mplstyle"

    # * DVC_tracked imports
    modelfunctions: Path = root / "models"

    # * DVC-tracked inputs
    experiments: Path = root / "experiments"
    notebooks: Path = root / "notebooks"
    rois: Path = root / "rois"
    samples: Path = root / "samples"
    sources: Path = root / "sources"

    # * DVC-tracked results
    contours: Path = root / "contours"
    examples: Path = root / "examples"
    filled: Path = root / "filled"
    lifetimes: Path = root / "lifetimes"
    tracks: Path = root / "tracks"
    unobstructed: Path = root / "unobstructed"
    # ! Previews
    previews: Path = root / "previews"
    binarized_preview: Path = previews / "binarized.nc"
    filled_preview: Path = previews / "filled.nc"
    gray_preview: Path = previews / "gray.nc"


class PackagePaths(DefaultPathsModel):
    """Package paths."""

    # * Git-tracked inputs
    # ! Package
    root: DirectoryPath = get_package_dir(boilercv_pipeline)
    models: DirectoryPath = root / "models"
    stages_literals: FilePath = models / "types" / "generated" / "stages.py"
    paths_module: FilePath = models / "paths.py"
    stages: dict[StageName, FilePath] = map_stages(root / "stages")  # pyright: ignore[reportAssignmentType]
    manual_stages: dict[ManualStageName, FilePath] = map_stages(root / "manual")  # pyright: ignore[reportAssignmentType]

    @model_validator(mode="before")
    @classmethod
    def sync_stages(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Validate paths."""
        if any(
            tuple(cls.model_fields[field].default) != get_args(literal)
            for field, literal in {
                "stages": StageName,
                "manual_stages": ManualStageName,
            }.items()
        ):
            sync_stages_literals()
        return data


def sync_stages_literals():
    """Sync stages literals."""
    paths = PackagePaths.model_fields
    stages_literals = paths["stages_literals"].default
    stages_literals.write_text(
        encoding="utf-8",
        data=dedent(f'''
            """Stages."""

            from typing import Literal, TypeAlias

            StageName: TypeAlias = Literal{list(paths["stages"].default)}
            """Stage."""
            ManualStageName: TypeAlias = Literal{list(paths["manual_stages"].default)}
            """Manual stage."""
            '''),
    )
    run(
        check=True,
        args=[
            "pwsh",
            "-Command",
            f"scripts/Initialize-Shell.ps1; ruff format {quote(stages_literals.as_posix())}",
        ],
    )
