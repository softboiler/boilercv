"""Documentation tools."""

import os
from pathlib import Path

from boilercore import WarningFilter, filter_certain_warnings

from boilercv_docs.patch_nbs import patch_nbs
from boilercv_tools.environment import init_shell

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
    init_shell()
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


def filter_boilercv_warnings():
    """Filter certain warnings for `boilercv`."""
    filter_certain_warnings(package="boilercv_pipeline", other_warnings=WARNING_FILTERS)
    for package in ["boilercv_docs", "boilercv_pipeline", "boilercv_tests"]:
        filter_certain_warnings(
            root_action=None, package=package, other_warnings=WARNING_FILTERS
        )


WARNING_FILTERS = [
    WarningFilter(
        category=DeprecationWarning,
        module="pybtex.plugin",
        message=r"pkg_resources is deprecated as an API\.",
    ),
    WarningFilter(
        category=DeprecationWarning,
        message=r"Deprecated call to `pkg_resources\.declare_namespace\('mpl_toolkits'\)`\.",
    ),
    WarningFilter(
        category=DeprecationWarning,
        message=r"Deprecated call to `pkg_resources\.declare_namespace\('sphinxcontrib'\)`\.",
    ),
    WarningFilter(
        category=DeprecationWarning,
        message=r"Deprecated call to `pkg_resources\.declare_namespace\('zc'\)`\.",
    ),
    WarningFilter(
        category=DeprecationWarning,
        module=r"latexcodec\.codec",
        message=r"open_text is deprecated\. Use files\(\) instead",
    ),
    WarningFilter(
        category=DeprecationWarning,
        module=r"nptyping\.typing_",
        message=r"`.+` is a deprecated alias for `.+`\.",
    ),
    WarningFilter(
        category=DeprecationWarning,
        module=r"IPython\.core\.pylabtools",
        message=r"backend2gui is deprecated.",
    ),
    *[
        WarningFilter(
            category=DeprecationWarning,
            message=rf"Deprecated call to `pkg_resources\.declare_namespace\('{ns}'\)`\.",
        )
        for ns in ["mpl_toolkits", "sphinxcontrib", "zc"]
    ],
    *[
        WarningFilter(
            category=DeprecationWarning, module=r"pytest_harvest.*", message=message
        )
        for message in [
            r"The hookspec pytest_harvest_xdist.+ uses old-style configuration options",
            r"The hookimpl pytest_configure uses old-style configuration options \(marks or attributes\)\.",
        ]
    ],
    WarningFilter(
        category=EncodingWarning, message="'encoding' argument not specified"
    ),
    *[
        WarningFilter(
            category=EncodingWarning,
            module=module,
            message=r"'encoding' argument not specified\.",
        )
        for module in [r"sphinx.*", r"jupyter_client\.connect"]
    ],
    WarningFilter(
        category=FutureWarning,
        message=r"A grouping was used that is not in the columns of the DataFrame and so was excluded from the result\. This grouping will be included in a future version of pandas\. Add the grouping as a column of the DataFrame to silence this warning\.",
    ),
    WarningFilter(
        # Happens during tests under some configurations
        message=r"ImportDenier\.find_spec\(\) not found; falling back to find_module\(\)",
        category=ImportWarning,
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
        category=RuntimeWarning,
        message=r"Proactor event loop does not implement add_reader family of methods required for zmq.+",
    ),
    WarningFilter(
        category=UserWarning,
        message=r"The palette list has more values \(\d+\) than needed \(\d+\), which may not be intended\.",
    ),
    WarningFilter(
        category=UserWarning,
        action="default",
        message=r"Loaded local environment variables from `\.env`",
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
