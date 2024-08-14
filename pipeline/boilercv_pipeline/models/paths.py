"""Parameter models for this project."""

from collections import defaultdict
from collections.abc import Callable
from functools import partial
from json import loads
from pathlib import Path
from typing import Annotated, Any, ClassVar

from pydantic import AfterValidator, field_validator
from pydantic.fields import FieldInfo

from boilercv_pipeline.contexts import ContextsModel
from boilercv_pipeline.contexts.types import (
    ContextsPluginSettings,
    PluginConfigDict,
    ValidationInfo,
)
from boilercv_pipeline.models.types import Kind, Model, RootContexts, Roots


def get_parser(model: type[Model]) -> Callable[[str], Model]:
    """Get parser for model or JSON-encoded string."""

    def parse(v: Model | str) -> Model:
        """Parse model or JSON-encoded string."""
        return model(**loads(v)) if isinstance(v, str) else v

    return parse


def make_directory(
    path: Path, info: ValidationInfo[RootContexts], key: str, file: bool
) -> Path:
    """Make directory."""
    if not path.is_absolute() and (root := getattr(info.context["roots"], key, None)):
        path = root / path
        directory = path.parent if file else path
        directory.mkdir(exist_ok=True, parents=True)
    return path


DataDir = Annotated[
    Path, AfterValidator(partial(make_directory, key="data", file=False))
]
"""Data directory path made upon validation."""
DataFile = Annotated[
    Path, AfterValidator(partial(make_directory, key="data", file=True))
]
"""Data file path made upon validation."""
DocsDir = Annotated[
    Path, AfterValidator(partial(make_directory, key="docs", file=False))
]
"""Docs directory path made upon validation."""
DocsFile = Annotated[
    Path, AfterValidator(partial(make_directory, key="docs", file=True))
]
"""Docs file path made upon validation."""


def get_config(
    data: Path | None = None, docs: Path | None = None
) -> PluginConfigDict[ContextsPluginSettings[RootContexts]]:
    """Get config for paths contexts."""
    return PluginConfigDict(
        plugin_settings=ContextsPluginSettings(
            contexts=RootContexts(roots=Roots(data=data, docs=docs))
        )
    )


class PathsContexts(ContextsModel):
    """Paths that ensures matches with default path types."""

    model_config: ClassVar[PluginConfigDict[ContextsPluginSettings[RootContexts]]] = (  # pyright: ignore[reportIncompatibleVariableOverride]
        get_config()
    )


class Paths(PathsContexts):
    """Paths relevant to the project."""

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
kind_validators: dict[tuple[str, bool], Kind] = {
    ("data", False): "DataDir",
    ("data", True): "DataFile",
    ("docs", False): "DocsDir",
    ("docs", True): "DocsFile",
}


def get_kind(field_info: FieldInfo) -> Kind | None:
    """Get kind."""
    if (
        (all_metadata := field_info.metadata)
        and (isinstance(meta := all_metadata[0], AfterValidator))
        and (kwds := getattr(meta.func, "keywords", None))
    ):
        return kind_validators.get(tuple(kwds.values()))  # pyright: ignore[reportArgumentType]


def get_kinds(paths: Paths) -> dict[Kind, list[Any]]:
    """Get kinds."""
    kinds = defaultdict(list)
    for info, value in zip(
        paths.model_fields.values(), paths.model_dump().values(), strict=True
    ):
        if kind := get_kind(info):
            kinds[kind].append(value)
            continue
        kinds["other"].append(value)
    return kinds


kinds = get_kinds(paths)


class MatchedPaths(PathsContexts):
    """Paths that ensures matches with default path types."""

    model_config = get_config(data=Path("data"), docs=Path("docs"))

    @field_validator("*", mode="before")
    @classmethod
    def validate_paths(cls, value: Any, info: ValidationInfo[RootContexts]) -> Any:
        """Model field type matches the default type."""
        if (
            (field_name := info.field_name)
            and (field_info := cls.model_fields.get(field_name))
            and (kind := get_kind(field_info))
            and (value not in kinds[kind])
        ):
            raise ValueError(
                f"Stage {cls.__name__} has path '{value}' of kind {kind} that doesn't match default paths."
            )
        return value
