"""Runtime types."""

from itertools import chain
from pathlib import Path
from shutil import rmtree
from typing import Annotated, TypeAlias

from pydantic import AfterValidator

from boilercv_docs.models.paths import rooted_paths

NbExecutionExcludePatterns: TypeAlias = Annotated[
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


SkipAutodoc: TypeAlias = Annotated[bool, AfterValidator(remove_stale_autodoc)]
