"""Models."""

from itertools import chain
from pathlib import Path
from shutil import rmtree
from typing import Annotated

from pydantic import AfterValidator, BaseModel

from boilercv_docs import get_root
from boilercv_docs.types import NbExecutionMode


def remove_stale_autodoc(skip_autodoc: bool) -> bool:
    """Remove stale autodoc products."""
    if skip_autodoc:
        rmtree(get_root() / "docs" / "apidocs", ignore_errors=True)
    return skip_autodoc


class Build(BaseModel):
    """Docs."""

    force_dev: bool = False
    """Force building documentation with dev-only data tracked by DVC."""
    nb_execution_excludepatterns: Annotated[
        list[str],
        AfterValidator(
            lambda patterns: [
                p.resolve().as_posix()
                for p in chain.from_iterable([
                    Path.cwd().glob(f"{pat}/**/*.ipynb") for pat in patterns
                ])
            ]
        ),
    ] = ["experiments", "notebooks"]
    """List of directories relative to `docs` to exclude executing notebooks in."""
    nb_execution_mode: NbExecutionMode = "off"
    """Notebook execution mode.

    https://myst-nb.readthedocs.io/en/stable/computation/execute.html#notebook-execution-modes
    """
    skip_autodoc: Annotated[bool, AfterValidator(remove_stale_autodoc)] = False
    """Skip the potentially slow process of autodoc generation."""
