from pathlib import Path

from cappa.base import command, invoke
from pydantic import DirectoryPath, Field

from boilercv_pipeline.models.deps import DaDepDir, DfDepDir
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.stages import Params, StagePaths
from boilercv_pipeline.models.types.runtime import DataDir, DocsFile

INCLUDE_PATTERNS: list[str] = [r"^2024-07-18.+$"]


class Contours(DfDepDir):
    path: DataDir = paths.contours
    include_patterns: list[str] = INCLUDE_PATTERNS


class Filled(DaDepDir):
    path: DataDir = paths.filled
    include_patterns: list[str] = INCLUDE_PATTERNS


class Deps(StagePaths):
    stage: DirectoryPath = Path(__file__).parent
    nb: DocsFile = paths.notebooks[stage.stem]
    contours: Contours = Field(default_factory=Contours)
    filled: Filled = Field(default_factory=Filled)


class Outs(StagePaths):
    dfs: DataDir = paths.e230920_objects


@command(
    invoke="boilercv_pipeline.stages.e230920_find_objects.__main__.main",
    default_long=True,
)
class E230920FindObjects(Params[Deps, Outs]):
    """Find objects."""

    deps: Deps = Field(default_factory=Deps)
    outs: Outs = Field(default_factory=Outs)


if __name__ == "__main__":
    invoke(E230920FindObjects)
