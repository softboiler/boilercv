"""Types."""

from pathlib import Path
from typing import Literal, TypeAlias

Kind: TypeAlias = Literal["DataDir", "DataFile", "DocsDir", "DocsFile"]
"""File or directory kind."""
Key: TypeAlias = Literal["data", "docs"]
"""Data or docs key."""
Kinds: TypeAlias = dict[Path, Kind]
"""Paths and their kinds."""
