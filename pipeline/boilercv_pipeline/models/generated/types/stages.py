"""Stages."""

from typing import Literal, TypeAlias

StageName: TypeAlias = Literal[
    "binarize",
    "convert",
    "e230920_find_contours",
    "e230920_find_objects",
    "e230920_find_tracks",
    "e230920_get_mae",
    "e230920_merge_mae",
    "e230920_merge_tracks",
    "e230920_plot_tracks",
    "e230920_process_tracks",
    "e230920_update_thermal_data",
    "fill",
    "find_contours",
    "flatten_data_dir",
    "preview_binarized",
    "preview_filled",
    "preview_gray",
]
"""Stage."""
