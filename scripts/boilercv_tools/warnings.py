"""Warnings."""

from typing import NamedTuple
from warnings import filterwarnings

from boilercv_tools.types import Action


def filter_boilercv_warnings():
    """Filter certain warnings for `boilercv`."""
    for filt in [
        WarningFilter(action="default"),
        *[
            WarningFilter(action="error", category=category, module=r"boilercv.*")
            for category in [
                DeprecationWarning,
                PendingDeprecationWarning,
                EncodingWarning,
            ]
        ],
        *WARNING_FILTERS,
    ]:
        filterwarnings(*filt)


class WarningFilter(NamedTuple):
    """A warning filter, e.g. to be unpacked into `warnings.filterwarnings`."""

    action: Action = "ignore"
    message: str = ""
    category: type[Warning] = Warning
    module: str = ""
    lineno: int = 0
    append: bool = False


WARNING_FILTERS = [
    # * --------------------------------------------------------------------------------
    # * MARK: DeprecationWarning
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
    # * --------------------------------------------------------------------------------
    # * MARK: EncodingWarning
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
    # * --------------------------------------------------------------------------------
    # * MARK: FutureWarning
    WarningFilter(
        category=FutureWarning,
        message=r"A grouping was used that is not in the columns of the DataFrame and so was excluded from the result\. This grouping will be included in a future version of pandas\. Add the grouping as a column of the DataFrame to silence this warning\.",
    ),
    # * --------------------------------------------------------------------------------
    # * MARK: ImportWarning
    WarningFilter(
        # Happens during tests under some configurations
        category=ImportWarning,
        message=r"ImportDenier\.find_spec\(\) not found; falling back to find_module\(\)",
    ),
    # * --------------------------------------------------------------------------------
    # * MARK: RuntimeWarning
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
    # * --------------------------------------------------------------------------------
    # * MARK: Combinations
    *[
        WarningFilter(
            category=category,
            # module=r"colorspacious\.comparison",  # ? CI still complains
            message=r"invalid escape sequence",
        )
        for category in [DeprecationWarning, SyntaxWarning]
    ],
]
"""Warning filters."""
