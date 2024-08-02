"""Documentation tools."""

import os
from pathlib import Path

from boilercv_docs.patch_nbs import patch_nbs
from boilercv_tools.environment import init_shell
from boilercv_tools.warnings import filter_boilercv_warnings

DOCS = Path("docs")
"""Docs directory."""
TEST_DATA = Path("tests/root")
"""Dependencies shared with tests."""
DOCS_DATA = Path("tests/root-docs")
"""Dependencies shared with tests."""
PYPROJECT = Path("pyproject.toml")
"""Path to `pyproject.toml`."""
CHECKS = [DOCS, TEST_DATA, DOCS_DATA, PYPROJECT]
"""Checks for the root directory."""


def init_docs_build() -> Path:
    """Initialize shell, ensure we are in `docs`, patch notebooks, return root."""
    filter_boilercv_warnings()
    root = get_root()
    init_shell(root)
    os.chdir(root / "docs")
    patch_nbs()
    return root


def get_root() -> Path:
    """Look for project root directory starting from current working directory."""
    path = Path().cwd()
    while not all((path / check).exists() for check in CHECKS):
        if path == (path := path.parent):
            raise RuntimeError("Project root directory not found.")
    return path
