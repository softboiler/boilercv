"""Contributor environment setup."""

import subprocess
from contextlib import chdir, nullcontext
from io import StringIO
from pathlib import Path
from shlex import quote
from sys import executable

from dotenv.main import DotEnv
from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    PyprojectTomlConfigSettingsSource,
    SettingsConfigDict,
)

import dev
from dev.modules import get_module_name


class Constants(BaseModel):
    """Constants for {mod}`~dev.tools.environment`."""

    dev_tool_config: tuple[str, ...] = ("tool", get_module_name(dev))
    """Path to `dev` tool configuration in `pyproject.toml`."""
    pylance_version_source: str = ".pylance-version"
    """Path to Pylance version file."""
    shell: list[str] = ["pwsh", "-Command"]
    """Shell invocation for running arbitrary commands."""
    uv_run_wrapper: str = "./Invoke-Uv.ps1"
    """Wrapper of `uv run` with extra setup."""
    env: str = ".env"
    """Name of environment file."""


const = Constants()


def sync_environment_variables(
    path: Path | None = None, pylance_version: str = "", setenv: bool = True
) -> str:
    """Sync `.env` with `pyproject.toml`, optionally setting environmetn variables."""
    path = Path(path) if path else Path.cwd() / ".env"
    config_dotenv = DotEnv(
        dotenv_path=None,
        stream=StringIO("\n".join(f"{k}={v}" for k, v in Config().env.items())),
    )
    dotenv = DotEnv(dotenv_path=path)
    if not dotenv._dict:  # noqa: SLF001
        dotenv._dict = {}  # noqa: SLF001
    if pylance_version:
        dotenv._dict["PYRIGHT_PYTHON_PYLANCE_VERSION"] = pylance_version  # noqa: SLF001  # pyright: ignore[reportOptionalSubscript]
    new: list[str] = []
    for key in DotEnv(dotenv_path=path).dict():
        if new_value := config_dotenv.get(key):
            dotenv._dict[key] = new_value  # noqa: SLF001
        else:
            new.append(key)
    for key in new:
        dotenv._dict[key]  # noqa: SLF001
    if setenv:
        dotenv.set_as_environment_variables()
    return "\n".join(f"{k}={v}" for k, v in config_dotenv.dict().items())


def run(*args: str):
    """Run command."""
    sep = " "
    with nullcontext() if Path(const.uv_run_wrapper).exists() else chdir(".."):
        subprocess.run(
            check=True, args=[*const.shell, sep.join([const.uv_run_wrapper, *args])]
        )


def run_dev(*args: str):
    """Run command from `dev` CLI."""
    run(f"& {quote(executable)} -m", *args)


def escape(path: str | Path) -> str:
    """Escape a path, suitable for passing to e.g. {func}`~subprocess.run`."""
    return quote(Path(path).as_posix())


class Config(BaseSettings):
    """Get tool config from `pyproject.toml`."""

    model_config = SettingsConfigDict(pyproject_toml_table_header=const.dev_tool_config)
    env: dict[str, str] = Field(default_factory=dict)

    @classmethod
    def settings_customise_sources(cls, settings_cls, **_):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Only load from `pyproject.toml`."""
        return (PyprojectTomlConfigSettingsSource(settings_cls),)
