"""Paths."""

from pathlib import Path

from boilercv_pipeline.config import const as pipeline_const
from boilercv_pipeline.config import get_root
from pydantic import BaseModel

from dev.tests.config import const as tests_const


class Constants(BaseModel):
    """Constants."""

    pyproject: Path = Path("pyproject.toml")
    docs: Path = Path("docs")


const = Constants()
"""Constants."""


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
