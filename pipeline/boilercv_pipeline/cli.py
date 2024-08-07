"""Command-line interface."""

from __future__ import annotations

from dataclasses import dataclass

from cappa.base import command
from cappa.subcommand import Subcommands


@command(invoke="boilercv_pipeline.models.Params")
class SyncParams:
    """Synchronize parameters."""


@command(invoke="boilercv_pipeline.models.paths.sync_stages_literals")
class SyncStagesLiterals:
    """Sync stages literals."""


@dataclass
class BoilercvPipeline:
    """Pipeline."""

    commands: Subcommands[SyncParams | SyncStagesLiterals]
