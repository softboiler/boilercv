"""Models."""

from pydantic import BaseModel

from dev.docs.models.types.runtime import NbExecutionExcludePatterns, SkipAutodoc
from dev.docs.types import BuildMode, NbExecutionMode


class Build(BaseModel):
    """Docs."""

    mode: BuildMode = None
    """Force building documentation in a certain mode."""
    nb_execution_excludepatterns: NbExecutionExcludePatterns = [
        "notebooks/e230920*.ipynb"
    ]
    """List of directories relative to `docs` to exclude executing notebooks in."""
    nb_execution_mode: NbExecutionMode = "off"
    """Notebook execution mode.

    https://myst-nb.readthedocs.io/en/stable/computation/execute.html#notebook-execution-modes
    """
    skip_autodoc: SkipAutodoc = False
    """Skip the potentially slow process of autodoc generation."""
    skip_autodoc_post_parse: bool = False
    """Skip the potentially slow process of autodoc post parsing."""