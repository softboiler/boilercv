"""Warnings."""

from collections.abc import Iterable

from boilercore.warnings import WarningFilter, filter_boiler_warnings

WARNING_FILTERS = []
"""Warning filters."""


def filter_boilercv_warnings(
    other_warnings: Iterable[WarningFilter] | None = WARNING_FILTERS,
    other_warnings_before: Iterable[WarningFilter] | None = None,
):
    """Filter certain warnings for `boilercv`."""
    filter_boiler_warnings(
        other_warnings=other_warnings, other_warnings_before=other_warnings_before
    )
