"""Stages."""

from typing import Literal, TypeAlias

StageName: TypeAlias = Literal[
    "compare_theory",
    "fill",
    "find_contours",
    "find_tracks",
    "find_unobstructed",
    "preview_binarized",
    "preview_filled",
    "preview_gray",
]
"""Stage."""
ManualStageName: TypeAlias = Literal["binarize", "convert", "flatten_data_dir"]
"""Manual stage."""
