"""Parameter models for this project."""

from pathlib import Path
from typing import get_args

from boilercv_pipeline.models.generated.types.stages import StageName
from boilercv_pipeline.models.path import (
    BoilercvPipelineContextStore,
    DataDir,
    DataFile,
    DocsFile,
    get_boilercv_pipeline_config,
)


class Paths(BoilercvPipelineContextStore):
    """Pipeline paths."""

    model_config = get_boilercv_pipeline_config(track_kinds=True)

    # * Local inputs
    cines: DataDir = Path("cines")
    hierarchical_data: DataDir = Path("hierarchical_data")
    large_examples: DataDir = Path("large_examples")
    large_sources: DataDir = Path("large_sources")
    notes: DataDir = Path("notes")
    sheets: DataDir = Path("sheets")
    # ! Uncompressed data
    uncompressed_contours: DataDir = Path("uncompressed_contours")
    uncompressed_filled: DataDir = Path("uncompressed_filled")
    uncompressed_sources: DataDir = Path("uncompressed_sources")
    # ! Examples
    example_cines: DataDir = Path("example_cines")
    large_example_cine: DataFile = example_cines / "2022-01-06T16-57-31.cine"

    # * Local results
    media: DataDir = Path("media")

    # * DVC-tracked imports
    modelfunctions: DataDir = Path("models")

    # * DVC-tracked inputs
    headers: DataDir = Path("headers")
    notebooks: dict[str | StageName, DocsFile] = {  # noqa: RUF012
        stage_name: Path("notebooks") / f"{stage_name}.ipynb"
        for stage_name in get_args(StageName)
    }
    samples: DataDir = Path("samples")
    sources: DataDir = Path("sources")
    thermal: DataDir = Path("thermal")

    # * DVC-tracked results
    rois: DataDir = Path("rois")
    contours: DataDir = Path("contours")
    examples: DataDir = Path("examples")
    filled: DataDir = Path("filled")

    e230920: DataDir = Path("e230920")

    e230920_thermal: DataFile = e230920 / Path("thermal.h5")
    e230920_thermal_plots: DataDir = e230920 / Path("thermal_plots")

    objects: DataDir = e230920 / Path("objects")
    objects_plots: DataDir = e230920 / Path("objects_plots")
    tracks: DataDir = e230920 / Path("tracks")
    tracks_plots: DataDir = e230920 / Path("tracks_plots")

    # ! Previews
    previews: DataDir = Path("previews")
    binarized_preview: DataFile = previews / "binarized_preview.nc"
    filled_preview: DataFile = previews / "filled_preview.nc"
    gray_preview: DataFile = previews / "gray_preview.nc"


paths = Paths()
