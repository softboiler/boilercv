"""Runtime types."""

from itertools import chain
from pathlib import Path
from shutil import rmtree
from typing import Annotated

from pydantic import AfterValidator

from boilercv_docs.models.paths import rooted_paths

NbExecutionExcludePatterns = Annotated[
    list[str],
    AfterValidator(
        lambda patterns: [
            p.resolve().as_posix()
            for p in chain.from_iterable([Path.cwd().glob(pat) for pat in patterns])
        ]
    ),
]


def remove_stale_autodoc(skip_autodoc: bool) -> bool:
    """Remove stale autodoc products."""
    if skip_autodoc:
        rmtree(rooted_paths.apidocs, ignore_errors=True)
    return skip_autodoc


SkipAutodoc = Annotated[bool, AfterValidator(remove_stale_autodoc)]
