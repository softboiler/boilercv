"""Command-line interface."""

from dataclasses import dataclass

from cappa.base import command, invoke
from cappa.subcommand import Subcommands

from boilercv_dev import SyncEnvironmentVariables


@command(invoke="boilercv_dev.tools.add_change")
class AddChange:
    """Add change."""


@command(invoke="boilercv_dev.tools.get_actions")
class GetActions:
    """Get actions used by this repository."""


@command(invoke="boilercv_dev.tools.sync_local_dev_configs")
class SyncLocalDevConfigs:
    """Synchronize local dev configs."""


@command(invoke="boilercv_dev.tools.elevate_pyright_warnings")
class ElevatePyrightWarnings:
    """Elevate Pyright warnings to errors."""


@command(invoke="boilercv_dev.tools.build_docs")
class BuildDocs:
    """Build docs."""


@command(invoke="boilercv_dev.docs.patch_notebooks.patch_notebooks")
class PatchNotebooks:
    """Build docs."""


@dataclass
class BoilercvDev:
    """Dev tools."""

    commands: Subcommands[
        SyncEnvironmentVariables
        | AddChange
        | GetActions
        | SyncLocalDevConfigs
        | ElevatePyrightWarnings
        | BuildDocs
        | PatchNotebooks
    ]


def main():
    """CLI entry-point."""
    invoke(BoilercvDev)


if __name__ == "__main__":
    main()
