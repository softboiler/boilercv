"""Command-line interface."""

from __future__ import annotations

from dataclasses import dataclass

from cappa.base import command, invoke
from cappa.subcommand import Subcommands


@command(invoke="boilercv_pipeline.models.Params")
class SyncParams:
    """Synchronize parameters."""


@command(invoke="boilercv_pipeline.manual.binarize.main")
class Binarize:
    """Binarize all videos and export their ROIs."""


@dataclass
class ManualStages:
    """Stages."""

    commands: Subcommands[Binarize]


@dataclass
class BoilercvPipeline:
    """Pipeline."""

    commands: Subcommands[SyncParams | ManualStages]


def main():
    """CLI entry-point."""
    invoke(BoilercvPipeline)


if __name__ == "__main__":
    main()
