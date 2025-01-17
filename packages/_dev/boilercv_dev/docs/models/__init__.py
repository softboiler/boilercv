"""Models."""

from pydantic import BaseModel

from boilercv_dev.docs.models.types import NbExecutionExcludePatterns, SkipAutodoc
from boilercv_dev.docs.types import BuildMode, NbExecutionMode


class Build(BaseModel):
    """Docs."""

    force_mode: BuildMode | None = None
    """Force building documentation in a certain mode."""
    nb_execution_excludepatterns: NbExecutionExcludePatterns = [
        "notebooks/e230920*.ipynb",
        "notebooks/get_mae.ipynb",
    ]
    """List of directories relative to `docs` to exclude executing notebooks in."""
    nb_execution_mode: NbExecutionMode = "cache"
    """Notebook execution mode.

    https://myst-nb.readthedocs.io/en/stable/computation/execute.html#notebook-execution-modes
    """
    skip_autodoc: SkipAutodoc = False
    """Skip the potentially slow process of autodoc generation."""
    skip_autodoc_post_parse: bool = False
    """Skip the potentially slow process of autodoc post parsing."""
