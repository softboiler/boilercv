"""Parameter models for this project."""

from pathlib import Path

from boilercore.fits import Fit
from boilercore.models import DefaultPathsModel, SynchronizedPathsYamlModel
from pydantic import DirectoryPath, FilePath

from boilercv_pipeline.config import const
from boilercv_pipeline.models.types.generated.stages import StageName


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
    # ! Previews
    previews: Path = root / "previews"
    binarized_preview: Path = previews / "binarized.nc"
    filled_preview: Path = previews / "filled.nc"
    gray_preview: Path = previews / "gray.nc"


class PackagePaths(DefaultPathsModel):
    """Package paths."""

    # * Git-tracked inputs
    # ! Package
    root: DirectoryPath = const.package_dir
    models: DirectoryPath = root / "models"
    stages_literals: FilePath = models / "types" / "generated" / "stages.py"
    paths_module: FilePath = models / "paths.py"
    stages: dict[StageName, FilePath] = const.stages  # pyright: ignore[reportAssignmentType]


class Params(SynchronizedPathsYamlModel):
    """Project parameters."""

    source: FilePath = Path.cwd() / "params.yaml"
    paths: Paths = Paths()
    package_paths: PackagePaths = PackagePaths()
    fit: Fit = Fit()
