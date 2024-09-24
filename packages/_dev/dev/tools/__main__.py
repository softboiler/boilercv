"""CLI for tools."""

from collections.abc import Collection
from json import dumps
from pathlib import Path
from re import finditer, sub
from shlex import join, split
from tomllib import loads

from cyclopts import App
from pydantic import BaseModel

from dev.tools import add_changes, environment
from dev.tools.environment import escape, run
from dev.tools.types import ChangeType


class Constants(BaseModel):
    """Constants for {mod}`~dev.tools.environment`."""

    pylance_version: str = Path(".pylance-version").read_text(encoding="utf-8").strip()
    """Pylance version."""


const = Constants()


APP = App(help_format="markdown")
"""CLI."""


def main():  # noqa: D103
    APP()


@APP.command
def sync_environment_variables(pylance_version: str = const.pylance_version):
    """Initialize shell."""
    log(environment.sync_environment_variables(pylance_version=pylance_version))


@APP.command
def add_change(change: ChangeType = "change"):
    """Add change."""
    add_changes.add_change(change)


@APP.command
def get_actions():
    """Get actions used by this repository.

    For additional security, select "Allow <user> and select non-<user>, actions and
    reusable workflows" in the General section of your Actions repository settings, and
    paste the output of this command into the "Allow specified actions and reusable
    workflows" block.

    Parameters
    ----------
    high
        Highest dependencies.
    """
    actions: list[str] = []
    for contents in [
        path.read_text("utf-8") for path in Path(".github/workflows").iterdir()
    ]:
        actions.extend([
            f"{match['action']}@*,"
            for match in finditer(r'uses:\s?"?(?P<action>.+)@', contents)
        ])
    log(sorted(set(actions)))


@APP.command
def sync_local_dev_configs():
    """Synchronize local dev configs to shadow `pyproject.toml`, with some changes.

    Duplicate pytest configuration from `pyproject.toml` to `pytest.ini`. These files
    shadow the configuration in `pyproject.toml`, which drives CI or if shadow configs
    are not present. Shadow configs are in `.gitignore` to facilitate local-only
    shadowing. Concurrent test runs are disabled in the local pytest configuration which
    slows down the usual local, granular test workflow.
    """
    config = loads(Path("pyproject.toml").read_text("utf-8"))
    pytest = config["tool"]["pytest"]["ini_options"]
    pytest["addopts"] = disable_concurrent_tests(pytest["addopts"])
    Path("pytest.ini").write_text(
        encoding="utf-8",
        data="\n".join(["[pytest]", *[f"{k} = {v}" for k, v in pytest.items()], ""]),
    )


def disable_concurrent_tests(addopts: str) -> str:
    """Normalize `addopts` string and disable concurrent pytest tests."""
    return sub(pattern=r"-n\s[^\s]+", repl="-n 0", string=join(split(addopts)))


@APP.command
def elevate_pyright_warnings():
    """Elevate Pyright warnings to errors."""
    config = loads(Path("pyproject.toml").read_text("utf-8"))
    pyright = config["tool"]["pyright"]
    for k, v in pyright.items():
        if (rule := k).startswith("report") and (_level := v) == "warning":
            pyright[rule] = "error"
    Path("pyrightconfig.json").write_text(
        encoding="utf-8", data=dumps(pyright, indent=2)
    )


@APP.command()
def build_docs():
    """Build docs."""
    run(
        "sphinx-autobuild --show-traceback docs _site",
        *[f"--ignore **/{p}" for p in ["temp", "data", "apidocs", "*schema.json"]],
    )


def log(obj):
    """Send object to `stdout`."""
    match obj:
        case str():
            print(obj)  # noqa: T201
        case Collection():
            for o in obj:
                log(o)
        case Path():
            log(escape(obj))
        case _:
            print(obj)  # noqa: T201


if __name__ == "__main__":
    main()
