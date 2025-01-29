"""Helper functions for tests."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from shlex import join, quote, split
from shutil import copy
from subprocess import run
from sys import executable
from tempfile import _RandomNameSequence  # pyright: ignore[reportAttributeAccessIssue]
from types import SimpleNamespace
from typing import Any

import pytest
from boilercore.hashes import hash_args
from boilercore.notebooks.namespaces import get_nb_ns
from boilercv_pipeline.models.params import set_display_options
from cachier import cachier  # pyright: ignore[reportMissingImports]
from seaborn import set_theme

from boilercv_dev.tests.types import Attributes, Params

NAMER: Iterator[str] = _RandomNameSequence()
"""Random name sequence for case files."""


def init():
    """Initialize test plot formats."""
    set_theme(context="notebook", style="whitegrid", palette="deep", font="sans-serif")
    set_display_options()


init()


@cachier(hash_func=partial(hash_args, get_nb_ns), separate_files=True)
def get_cached_nb_ns(
    nb: str, params: Params | None = None, attributes: Attributes | None = None
) -> SimpleNamespace:
    """Get cached notebook namespace."""
    return get_nb_ns(nb, params or {}, attributes or [])


@dataclass
class Case:
    """Notebook test case.

    Args:
        stage: Notebook stage.
        suffix: Test ID suffix.
        params: Parameters to pass to the notebook.
    """

    stage: str
    """Notebook stage."""
    id: str = "_"
    """Test ID suffix."""
    params: dict[str, Any] = field(default_factory=dict)
    """Parameters to pass to the notebook."""
    results: list[str] = field(default_factory=list)
    """Additional results to get from the notebook."""
    marks: Sequence[pytest.Mark] = field(default_factory=list)
    """Pytest marks."""
    clean_path: Path | None = field(default=None, init=False)
    """Path to the cleaned notebook."""

    @property
    def path(self) -> Path:
        """Notebook path."""
        return Path("docs") / "notebooks" / f"{self.stage}.ipynb"

    @property
    def nb(self) -> str:
        """Notebook contents."""
        return self.path.read_text(encoding="utf-8") if self.path.exists() else ""

    def clean_nb(self) -> str:
        """Clean notebook contents."""
        (test_temp_nbs := Path("docs") / "temp").mkdir(exist_ok=True, parents=True)
        self.clean_path = (test_temp_nbs / next(NAMER)).with_suffix(".ipynb")
        copy(self.path, self.clean_path)
        clean_notebooks(self.clean_path)
        return self.clean_path.read_text(encoding="utf-8")


def parametrize_by_cases(*cases: Case):
    """Parametrize this test by cases."""
    return pytest.mark.parametrize(
        "ns", [pytest.param(c, marks=c.marks, id=c.id) for c in cases], indirect=["ns"]
    )


@dataclass
class Caser:
    """Notebook test case generator."""

    exp: Path
    cases: list[Case] = field(default_factory=list)

    def __call__(
        self,
        stage: str,
        id: str = "_",
        params: dict[str, Any] | None = None,
        results: list[str] | None = None,
        marks: Sequence[pytest.Mark] | None = None,
    ) -> Case:
        """Add case to experiment."""
        case = Case(
            stage=stage,
            id=id,
            params=params or {},
            results=results or [],
            marks=marks or [],
        )
        self.cases.append(case)
        return case


def clean_notebooks(*nbs: Path | str):  # pyright: ignore[reportRedeclaration]
    """Clean notebooks using pre-commit hooks."""
    nbs: str = join(str(nb) for nb in nbs)
    files = f"--files {nbs}"
    quote((Path(executable).parent / "pre-commit").as_posix())
    for cmd in [
        split(
            f"{quote((Path(executable).parent / 'pre-commit').as_posix())} run {subcmd}"
        )
        for subcmd in [f"nb-clean {files}", f"ruff {files}", f"ruff-format {files}"]
    ]:
        run(cmd, check=False)  # noqa: S603
