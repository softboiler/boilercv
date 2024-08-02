"""Warnings."""

from boilercore.warnings import filter_boiler_warnings


def filter_boilercv_warnings():
    """Filter certain warnings for `boilercv`."""
    filter_boiler_warnings(other_warnings=WARNING_FILTERS)


WARNING_FILTERS = []
"""Warning filters."""
