"""Contributor environment."""

import subprocess
from collections.abc import Sequence
from os import environ
from pathlib import Path
from shlex import quote, split
from sys import platform
from warnings import warn

from _pytest.config import _prepareconfig
from dotenv import load_dotenv
from pytest_env.plugin import pytest_load_initial_conftests


def init_shell():
    """Initialize shell."""
    if load_dotenv():
        warn("Loaded local environment variables from `.env`", stacklevel=2)
    if ((bin_ := Path("bin").resolve()).exists()) and (path := environ.get("PATH")):
        environ["PATH"] = f"{bin_}{';' if platform == 'win32' else ':'}{path}"
    pytest_load_initial_conftests(
        [],
        config := _prepareconfig(args=[], plugins=[]),
        config._parser,  # noqa: SLF001
    )


def run(args: str | Sequence[str]):
    """Build docs."""
    sep = " "
    subprocess.run(
        check=True,
        args=split(
            sep.join([
                "pwsh -Command",
                f"{get_venv_activator()};",
                *([args] if isinstance(args, str) else args),
            ])
        ),
    )


def get_venv_activator():
    """Get virtual environment activator."""
    return (
        escape(activate)
        if (
            activate := (
                Path(".venv/scripts/activate.ps1")
                if platform == "win32"
                else Path(".venv/bin/activate.ps1")
            )
        ).exists()
        else ""
    )


def escape(path: str | Path) -> str:
    """Escape a path, suitable for passing to e.g. {func}`~subprocess.run`."""
    return quote(Path(path).as_posix())
