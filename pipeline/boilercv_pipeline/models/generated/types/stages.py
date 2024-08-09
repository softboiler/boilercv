"""Stages."""

from typing import Literal, TypeAlias

StageName: TypeAlias = Literal[
    "binarize",
    "convert",
    "fill",
    "find_contours",
    "flatten_data_dir",
    "preview_binarized",
    "preview_filled",
    "preview_gray",
]
"""Stage."""
