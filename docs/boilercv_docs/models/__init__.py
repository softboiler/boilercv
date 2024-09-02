"""Models."""

from pydantic import BaseModel

from boilercv_docs.models.types.runtime import NbExecutionExcludePatterns, SkipAutodoc
from boilercv_docs.types import BuildMode, NbExecutionMode


class Build(BaseModel):
    """Docs."""

    mode: BuildMode = None
    """Force building documentation in a certain mode."""
    nb_execution_excludepatterns: NbExecutionExcludePatterns = [
        "notebooks/e230920*.ipynb",
        "notebooks/find_objects.ipynb",
    ]
    """List of directories relative to `docs` to exclude executing notebooks in."""
    # TODO: Set to `cache` after fixing notebooks
    nb_execution_mode: NbExecutionMode = "cache"
    """Notebook execution mode.

    https://myst-nb.readthedocs.io/en/stable/computation/execute.html#notebook-execution-modes
    """
    skip_autodoc: SkipAutodoc = False
    """Skip the potentially slow process of autodoc generation."""
    skip_autodoc_post_parse: bool = False
    """Skip the potentially slow process of autodoc post parsing."""
