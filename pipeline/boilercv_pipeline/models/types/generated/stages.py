"""Stages."""

from typing import Literal, TypeAlias

StageName: TypeAlias = Literal[
    "fill",
    "find_contours",
    "preview_binarized",
    "preview_filled",
    "preview_gray",
    "common_preview",
]
"""Stage."""
