"""Helper functions for tests."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass, field
from functools import partial
from itertools import chain
from pathlib import Path
from shlex import join, quote, split
from shutil import copy
from subprocess import run
from sys import executable
from tempfile import _RandomNameSequence  # pyright: ignore[reportAttributeAccessIssue]
from types import SimpleNamespace
from typing import Any

import pytest
from _pytest.mark.structures import ParameterSet
from boilercore.hashes import hash_args
from boilercore.notebooks.namespaces import get_nb_ns
from boilercore.paths import get_module_name, get_module_rel, walk_modules
from cachier import cachier  # pyright: ignore[reportMissingImports]
from matplotlib.pyplot import style
from seaborn import set_theme

import boilercv_pipeline
from boilercv_tests.types import Attributes, Params

PACKAGE = get_module_name(boilercv_pipeline)
"""Name of the package to test."""
MPLSTYLE = Path("data/plotting/base.mplstyle")
"""Styling for test plots."""
NAMER: Iterator[str] = _RandomNameSequence()
"""Random name sequence for case files."""
TEST_TEMP_NBS = Path("docs/temp")
"""Temporary notebooks directory."""
TEST_TEMP_NBS.mkdir(exist_ok=True)


def init():
    """Initialize test plot formats."""
    set_theme(context="notebook", style="whitegrid", palette="deep", font="sans-serif")
    style.use(style=MPLSTYLE)


init()


def get_nb(exp: Path, name: str) -> Path:
    """Get notebook path for experiment and name."""
    return (exp / name).with_suffix(".ipynb")


@cachier(hash_func=partial(hash_args, get_nb_ns), separate_files=True)
def get_cached_nb_ns(
    nb: str, params: Params | None = None, attributes: Attributes | None = None
) -> SimpleNamespace:
    """Get cached notebook namespace."""
    return get_nb_ns(nb, params or {}, attributes or [])


boilercv_pipeline_dir = Path("pipeline") / PACKAGE
STAGES: list[ParameterSet] = []
for module in walk_modules(boilercv_pipeline_dir):
    if module.startswith("boilercv_pipeline.manual"):
        stage = get_module_rel(module, "manual")
        match stage.split("."):
            case ("generate_experiment_docs", *_):
                marks = [pytest.mark.skip(reason="Local-only documentation.")]
            case ("update_experiments_from_docs", *_):
                marks = [pytest.mark.skip(reason="Local-only documentation.")]
            case _:
                marks = []
        STAGES.append(
            pytest.param(module, id=get_module_rel(module, PACKAGE), marks=marks)
        )
        continue
    if not module.startswith("boilercv_pipeline.stages"):
        continue
    stage = get_module_rel(module, "stages")
    match stage.split("."):
        case ("experiments", "e230920_subcool", *_):
            marks = [pytest.mark.skip(reason="Test data missing.")]
        case ("generate_reports", *_):
            marks = [pytest.mark.skip(reason="Local-only documentation.")]
        case ("compare_theory" | "find_tracks" | "find_unobstructed", *_):
            marks = [pytest.mark.skip(reason="Implementation trivially does nothing.")]
        case _:
            marks = []
    STAGES.append(pytest.param(module, id=get_module_rel(module, PACKAGE), marks=marks))


@dataclass
class Case:
    """Notebook test case.

    Args:
        path: Path to the notebook.
        suffix: Test ID suffix.
        params: Parameters to pass to the notebook.
        results: Variable names to retrieve and optional expectations on their values.
    """

    path: Path
    """Path to the notebook."""
    clean_path: Path | None = field(default=None, init=False)
    """Path to the cleaned notebook."""
    id: str = "_"
    """Test ID suffix."""
    params: dict[str, Any] = field(default_factory=dict)
    """Parameters to pass to the notebook."""
    results: dict[str, Any] = field(default_factory=dict)
    """Variable names to retrieve and optional expectations on their values."""
    marks: Sequence[pytest.Mark] = field(default_factory=list)
    """Pytest marks."""

    @property
    def nb(self) -> str:
        """Notebook contents."""
        return self.path.read_text(encoding="utf-8") if self.path.exists() else ""

    def clean_nb(self) -> str:
        """Clean notebook contents."""
        self.clean_path = (TEST_TEMP_NBS / next(NAMER)).with_suffix(".ipynb")
        copy(self.path, self.clean_path)
        clean_notebooks(self.clean_path)
        return self.clean_path.read_text(encoding="utf-8")

    def get_ns(self) -> SimpleNamespace:
        """Get notebook namespace for this check."""
        return get_nb_ns(nb=self.nb, params=self.params, attributes=self.results)


def normalize_cases(*cases: Case) -> Iterable[Case]:
    """Normalize cases to minimize number of caches.

    Assign the same results to cases with the same path and parameters, preserving
    expectations. Sort parameters and results.

    Parameters
    ----------
    *cases
        Cases to normalize.

    Returns
    -------
    Normalized cases.
    """
    seen: dict[Path, dict[str, Any]] = {}
    all_cases: list[list[Case]] = []
    # Find cases with the same path and parameters and sort parameters
    for c in cases:
        for i, (path, params) in enumerate(seen.items()):
            if c.path == path and c.params == params:
                all_cases[i].append(c)
                break
        else:
            # If the loop doesn't break, no match was found
            seen[c.path] = c.params
            all_cases.append([c])
        c.params = dict(sorted(c.params.items()))
    # Assign the same results to common casees and sort results
    for cs in all_cases:
        all_results: set[str] = set()
        all_results.update(chain.from_iterable(c.results.keys() for c in cs))
        for c in cs:
            c.results |= {r: None for r in all_results if r not in c.results}
            c.results = dict(sorted(c.results.items()))
    return cases


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
        name: str,
        id: str = "_",  # noqa: A002
        params: dict[str, Any] | None = None,
        results: dict[str, Any] | Iterable[Any] | None = None,
        marks: Sequence[pytest.Mark] | None = None,
    ) -> Case:
        """Add case to experiment."""
        if results:
            results = results if isinstance(results, dict) else dict.fromkeys(results)
        else:
            results = {}
        case = Case(get_nb(self.exp, name), id, params or {}, results, marks or [])
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
