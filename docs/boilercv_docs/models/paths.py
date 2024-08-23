"""Paths."""

from pathlib import Path

from pydantic import BaseModel

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
    while (path / "conf.py").exists() or not all(
        (path / check).exists() for check in [const.pyproject, const.docs]
    ):
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
