"""Config."""

from collections import defaultdict
from collections.abc import Callable
from functools import partial
from typing import Any

from pydantic import AfterValidator, BaseModel
from pydantic.fields import FieldInfo

from boilercv_pipeline.models import Paths
from boilercv_pipeline.root_contexts import make_absolute_directory, make_absolute_file


def get_kind(
    field_info: FieldInfo, kind_validators: dict[tuple[Callable[..., Any], str], str]
) -> str | None:
    """Get kind."""
    if (
        (all_metadata := field_info.metadata)  # noqa: PLR0916
        and (isinstance(meta := all_metadata[0], AfterValidator))
        and (kwds := getattr(meta.func, "keywords", None))
        and (isinstance((func := meta.func), partial))
        and (key := kwds.get("key"))
        and (kind := kind_validators.get((func.func, key)))
    ):
        return kind


def get_kinds(
    paths: Paths, kind_validators: dict[tuple[Callable[..., Any], str], str]
) -> dict[str, list[Any]]:
    """Get kinds."""
    kinds: dict[str, list[Any]] = defaultdict(list)
    for info, value in zip(
        Paths.model_fields.values(), paths.model_dump().values(), strict=True
    ):
        if kind := get_kind(info, kind_validators):
            kinds[kind].append(value)
            continue
        kinds["other"].append(value)
    return kinds


class Settings(BaseModel):
    """Settings."""

    paths: Paths = Paths()
    kind_validators: dict[tuple[Callable[..., Any], str], str] = {
        (make_absolute_directory, "data"): "DataDir",
        (make_absolute_file, "data"): "DataFile",
        (make_absolute_directory, "docs"): "DocsDir",
        (make_absolute_file, "docs"): "DocsFile",
    }
    kinds: dict[str, list[Any]] = get_kinds(paths, kind_validators)


default = Settings()
