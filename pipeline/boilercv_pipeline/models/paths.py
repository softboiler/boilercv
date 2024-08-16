"""Parameter models for this project."""

from pathlib import Path

from boilercv_pipeline.models.types.runtime import (
    ROOTED,
    BoilercvPipelineCtxModel,
    DataDir,
    DataFile,
    DocsDir,
    get_boilercv_pipeline_config,
)


class Paths(BoilercvPipelineCtxModel):
    """Pipeline paths."""

    model_config = get_boilercv_pipeline_config(track_kinds=True)

    # * Local inputs
    cines: DataDir = Path("cines")
    hierarchical_data: DataDir = Path("hierarchical_data")
    large_examples: DataDir = Path("large_examples")
    large_sources: DataDir = Path("large_sources")
    notes: DataDir = Path("notes")
    profiles: DataDir = Path("profiles")
    sheets: DataDir = Path("sheets")
    # ! Uncompressed data
    uncompressed_contours: DataDir = Path("uncompressed_contours")
    uncompressed_filled: DataDir = Path("uncompressed_filled")
    uncompressed_sources: DataDir = Path("uncompressed_sources")
    # ! Examples
    example_cines: DataDir = Path("example_cines")
    large_example_cine: DataFile = example_cines / "2022-01-06T16-57-31.cine"

    # * Local results
    docx: DataDir = Path("docx")
    html: DataDir = Path("html")
    md: DataDir = Path("md")
    media: DataDir = Path("media")

    # * Git-tracked inputs
    # ! Plotting config
    plot_config: DataDir = Path("plotting")
    mpl_base: DataFile = plot_config / "base.mplstyle"
    mpl_hide_title: DataFile = plot_config / "hide_title.mplstyle"

    # * DVC_tracked imports
    modelfunctions: DataDir = Path("models")

    # * DVC-tracked inputs
    notebooks: DataDir = Path("notebooks")
    rois: DataDir = Path("rois")
    samples: DataDir = Path("samples")
    sources: DataDir = Path("sources")
    e230920_thermal_raw: DataFile = Path("e230920_thermal_raw.csv")

    # * DVC-tracked results
    contours: DataDir = Path("contours")
    examples: DataDir = Path("examples")
    filled: DataDir = Path("filled")
    lifetimes: DataDir = Path("lifetimes")
    e230920_thermal: DataFile = Path("e230920_thermal.h5")
    e230920_contours: DataDir = Path("e230920_contours")
    e230920_objects: DataDir = Path("e230920_objects")
    e230920_tracks: DataDir = Path("e230920_tracks")
    e230920_processed_tracks: DataDir = Path("e230920_processed_tracks")
    e230920_merged_tracks: DataFile = Path("e230920_merged_tracks.h5")
    e230920_mae: DataDir = Path("e230920_mae")
    e230920_merged_mae: DataFile = Path("e230920_merged_mae.h5")

    # ! Previews
    previews: DataDir = Path("previews")
    binarized_preview: DataFile = previews / "binarized_preview.nc"
    filled_preview: DataFile = previews / "filled_preview.nc"
    gray_preview: DataFile = previews / "gray_preview.nc"

    e230920_notebooks: DocsDir = Path("experiments") / "e230920"


paths = Paths()


class StagePaths(BoilercvPipelineCtxModel):
    """Paths for stages."""

    model_config = get_boilercv_pipeline_config(
        ROOTED, kinds_from=paths, track_kinds=True
    )
