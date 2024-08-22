"""Models."""

from itertools import chain
from pathlib import Path
from shutil import rmtree
from typing import Annotated

from pydantic import AfterValidator, BaseModel

from boilercv_docs.types import BuildMode, NbExecutionMode
from boilercv_pipeline.config import const as pipeline_const
from boilercv_tests.config import const as tests_const


class Constants(BaseModel):
    """Constants."""

    pyproject: Path = Path("pyproject.toml")
    docs: Path = Path("docs")


const = Constants()
"""Constants."""


def get_root() -> Path:
    """Look for project root directory starting from current working directory."""
    path = Path().cwd()
    while not all((path / check).exists() for check in [const.pyproject, const.docs]):
        if path == (path := path.parent):
            raise RuntimeError("Project root directory not found.")
    return path


class RootedPaths(BaseModel):
    """Paths."""

    root: Path = get_root()
    pyproject: Path = root / const.pyproject
    docs: Path = root / const.docs
    apidocs: Path = docs / "apidocs"
    notebooks: Path = docs / "notebooks"
    docs_data: Path = docs / "data"
    test_data: Path = root / tests_const.data
    pipeline_data: Path = root / pipeline_const.data


rooted_paths = RootedPaths()


def remove_stale_autodoc(skip_autodoc: bool) -> bool:
    """Remove stale autodoc products."""
    if skip_autodoc:
        rmtree(rooted_paths.apidocs, ignore_errors=True)
    return skip_autodoc


class Build(BaseModel):
    """Docs."""

    mode: BuildMode = None
    """Force building documentation in a certain mode."""
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
