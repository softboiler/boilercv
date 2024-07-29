"""Documentation tools."""

import os
from pathlib import Path

from boilercore import WarningFilter

from boilercv_docs.patch_nbs import patch_nbs

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


def chdir_docs() -> Path:
    """Ensure we are in the `docs` directory and return the root directory."""
    root = get_root()
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


warning_filters = [
    WarningFilter(
        category=FutureWarning,
        message=r"A grouping was used that is not in the columns of the DataFrame and so was excluded from the result\. This grouping will be included in a future version of pandas\. Add the grouping as a column of the DataFrame to silence this warning\.",
    ),
    WarningFilter(
        category=RuntimeWarning, message=r"invalid value encountered in power"
    ),
    WarningFilter(
        # ? https://github.com/pytest-dev/pytest-qt/issues/558#issuecomment-2143975018
        category=RuntimeWarning,
        message=r"Failed to disconnect .* from signal",
    ),
    WarningFilter(
        category=RuntimeWarning,
        message=r"numpy\.ndarray size changed, may indicate binary incompatibility\. Expected \d+ from C header, got \d+ from PyObject",
    ),
    WarningFilter(
        category=UserWarning,
        message=r"The palette list has more values \(\d+\) than needed \(\d+\), which may not be intended\.",
    ),
    WarningFilter(
        category=UserWarning,
        message=r"To output multiple subplots, the figure containing the passed axes is being cleared\.",
    ),
    *[
        WarningFilter(
            message=r"invalid escape sequence",
            category=category,
            # module=r"colorspacious\.comparison",  # ? CI still complains
        )
        for category in [DeprecationWarning, SyntaxWarning]
    ],
]
"""Warning filters for documentation notebooks."""
