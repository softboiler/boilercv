"""Dev."""

from collections.abc import Collection
from pathlib import Path
from shlex import quote

from cappa.base import command


def escape(path: str | Path) -> str:
    """Escape a path, suitable for passing to e.g. {func}`~subprocess.run`."""
    return quote(Path(path).as_posix())


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


@command(invoke="boilercv_dev.tools.environment.sync_environment_variables")
class SyncEnvironmentVariables:
    """Sync `.env` with `pyproject.toml`."""

    config_only: bool = False
    """Only get the config environment variables."""
