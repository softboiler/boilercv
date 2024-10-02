"""Command-line interface."""

from __future__ import annotations

from dataclasses import dataclass

from cappa.subcommand import Subcommands

from boilercv_pipeline.cli.experiments import Trackpy
from boilercv_pipeline.cli.sync_dvc import SyncDVC
from boilercv_pipeline.cli.types import Stages


@dataclass
class Stage:
    """Run a pipeline stage."""

    commands: Subcommands[Stages]


@dataclass
class Exp:
    """Run a pipeline experiment."""

    commands: Subcommands[Trackpy]


@dataclass
class BoilercvPipeline:
    """Run the research data pipeline."""

    commands: Subcommands[SyncDVC | Stage | Exp]
