"""Stages."""

from typing import Literal, TypeAlias

StageName: TypeAlias = Literal[
    "binarize",
    "convert",
    "fill",
    "find_contours",
    "find_objects",
    "find_tracks",
    "get_thermal_data",
    "preview_binarized",
    "preview_filled",
    "preview_gray",
    "skip_cloud",
]
"""Stage."""
