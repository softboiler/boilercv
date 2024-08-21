from pydantic import Field

from boilercv.data import FRAME
from boilercv_pipeline.models.deps import DaSlicer, first_slicer
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.types.runtime import DataDir
from boilercv_pipeline.stages import e230920_find_objects
from boilercv_pipeline.stages.e230920_find_objects.__main__ import main

OVERRIDE_INCLUDE_PATTERNS = Field(default_factory=list)
INCLUDE = Field(default=["2024-07-18T17-44-35"])


class Contours(e230920_find_objects.Contours):
    path: DataDir = paths.contours
    include_patterns: list[str] = OVERRIDE_INCLUDE_PATTERNS
    include: list[str] = INCLUDE


class Filled(e230920_find_objects.Filled):
    path: DataDir = paths.filled
    include_patterns: list[str] = OVERRIDE_INCLUDE_PATTERNS
    include: list[str] = INCLUDE
    slicer_patterns: dict[str, DaSlicer] = {r".+": {FRAME: first_slicer(n=3, step=10)}}  # noqa: RUF012


class Deps(e230920_find_objects.Deps):
    contours: Contours = Field(default_factory=Contours)  # pyright: ignore[reportIncompatibleVariableOverride]
    filled: Filled = Field(default_factory=Filled)  # pyright: ignore[reportIncompatibleVariableOverride]


class E230920FindObjects(e230920_find_objects.E230920FindObjects):
    deps: Deps = Field(default_factory=Deps)  # pyright: ignore[reportIncompatibleVariableOverride]


if __name__ == "__main__":
    main(E230920FindObjects())
