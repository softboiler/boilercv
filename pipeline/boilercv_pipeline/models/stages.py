"""Stage models."""

from pathlib import Path
from typing import Generic, TypeAlias, TypeVar

from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.models.types.runtime import (
    BoilercvPipelineCtxModel,
    Roots,
    get_boilercv_pipeline_config,
)

ROOTED = Roots(data=Path("data"), docs=Path("docs"))
"""Paths rooted to their directories."""


class Stage(BoilercvPipelineCtxModel):
    """Base of stage models."""

    model_config = get_boilercv_pipeline_config(
        ROOTED, kinds_from=paths, track_kinds=True
    )


class StagePaths(Stage):
    """Paths for stage dependencies and outputs."""


Deps_T = TypeVar("Deps_T", bound=StagePaths, covariant=True)
"""Dependencies type."""
Outs_T = TypeVar("Outs_T", bound=StagePaths, covariant=True)
"""Outputs type."""


class Params(BoilercvPipelineCtxModel, Generic[Deps_T, Outs_T]):
    """Stage parameters."""

    deps: Deps_T
    """Stage dependencies."""
    outs: Outs_T
    """Stage outputs."""


class NbDeps(StagePaths):
    """Stage dependencies including a notebook."""

    nb: Path


NbDeps_T = TypeVar("NbDeps_T", bound=NbDeps, covariant=True)
"""Notebook dependencies type."""


class DfsOuts(StagePaths):
    """Notebook outputs with dataframe outputs."""

    dfs: Path


DfsOuts_T = TypeVar("DfsOuts_T", bound=DfsOuts, covariant=True)
"""Notebook outputs with a dataframe type."""


class NbParams(Params[NbDeps_T, Outs_T], Generic[NbDeps_T, Outs_T]):
    """Stage parameters with a notebook in its dependencies."""


AnyNbParams: TypeAlias = NbParams[NbDeps, DfsOuts]


class E230920Params(NbParams[NbDeps_T, DfsOuts_T], Generic[NbDeps_T, DfsOuts_T]):
    """Parameters for `e230920` stages."""

    pattern: str = r"^2024-07-18.+$"
    time: str = "2024-07-18T17-44-35"


AnyE230920Params: TypeAlias = E230920Params[NbDeps, DfsOuts]
