"""Types."""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import TypeAlias


@dataclass
class Out:
    """Output."""

    key: str
    path: Path | None = None
    suffix: str = ""
    attr: str = "outs"

    @property
    def stem(self):
        """Name."""
        return f"{self.key}_{self.suffix}"


NbProcess: TypeAlias = Callable[[SimpleNamespace, Out], None]
"""Notebook process."""
