from pathlib import Path

from cappa.base import command, invoke
from pydantic import DirectoryPath, Field

from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.stages import DfsOuts, E230920Params, NbDeps
from boilercv_pipeline.models.types.runtime import DataDir, DocsFile


class Deps(NbDeps):
    stage: DirectoryPath = Path(__file__).parent
    nb: DocsFile = paths.notebooks[stage.stem]
    contours: DataDir = paths.contours


class Outs(DfsOuts):
    dfs: DataDir = paths.e230920_contours


@command(
    invoke="boilercv_pipeline.stages.e230920_find_contours.__main__.main",
    default_long=True,
)
class E230920FindContours(E230920Params[Deps, Outs]):
    """Update thermal data for the experiment."""

    deps: Deps = Field(default_factory=Deps)
    outs: Outs = Field(default_factory=Outs)


if __name__ == "__main__":
    invoke(E230920FindContours)
