"""Command-line interface."""

from __future__ import annotations

from dataclasses import dataclass

from cappa.subcommand import Subcommands

from boilercv_pipeline.cli.sync_dvc import SyncDVC
from boilercv_pipeline.cli.types import Stages


@dataclass
class Stage:
    """Pipeline stage."""

    commands: Subcommands[Stages]


@dataclass
class BoilercvPipeline:
    """Pipeline."""

    commands: Subcommands[SyncDVC | Stage]
