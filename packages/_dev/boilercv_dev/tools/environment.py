"""Contributor environment setup."""

import subprocess
from contextlib import chdir, nullcontext
from io import StringIO
from os import environ
from pathlib import Path

from dotenv import dotenv_values, load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    PyprojectTomlConfigSettingsSource,
    SettingsConfigDict,
)

import boilercv_dev
from boilercv_dev.docs.models.paths import rooted_paths
from boilercv_dev.modules import get_module_name


class Constants(BaseModel):
    """Constants for {mod}`~dev.tools.environment`."""

    dev_tool_config: tuple[str, ...] = ("tool", get_module_name(boilercv_dev))
    """Path to `dev` tool configuration in `pyproject.toml`."""
    pylance_version_source: str = ".pylance-version"
    """Path to Pylance version file."""
    shell: list[str] = ["pwsh", "-Command"]
    """Shell invocation for running arbitrary commands."""
    uv_run_wrapper: str = "./Invoke-Uv.ps1"
    """Wrapper of `uv run` with extra setup."""
    env: Path = (
        Path(environ["GITHUB_ENV"])
        if environ.get("GITHUB_ENV")
        else rooted_paths.root / ".env"
    )
    """Environment file path."""
    pylance_version: str = (
        (rooted_paths.root / ".pylance-version").read_text(encoding="utf-8").strip()
    )
    """Pylance version."""


const = Constants()


def sync_environment_variables(
    path: Path | None = None,
    pylance_version: str = const.pylance_version,
    setenv: bool = True,
):
    """Sync `.env` with `pyproject.toml`, optionally setting environment variables."""
    path = Path(path) if path else Path.cwd() / ".env"
    config_env = Config().env
    if pylance_version:
        config_env["PYRIGHT_PYTHON_PYLANCE_VERSION"] = pylance_version
    dotenv = dotenv_values(const.env)
    keys_set: list[str] = []
    for key in dotenv:
        if override := config_env.get(key):
            keys_set.append(key)
            dotenv[key] = override
    for k, v in config_env.items():
        if k not in keys_set:
            dotenv[k] = v
    if setenv:
        load_dotenv(stream=StringIO("\n".join(f"{k}={v}" for k, v in dotenv.items())))
    const.env.write_text(
        encoding="utf-8", data="\n".join(f"{k}={v}" for k, v in dotenv.items())
    )


def run(*args: str, check: bool = True, **kwds):
    """Run command."""
    sep = " "
    with nullcontext() if Path(const.uv_run_wrapper).exists() else chdir(".."):
        subprocess.run(
            check=check,
            args=[*const.shell, sep.join([const.uv_run_wrapper, *args])],
            **kwds,
        )


class Config(BaseSettings):
    """Get tool config from `pyproject.toml`."""

    model_config = SettingsConfigDict(pyproject_toml_table_header=const.dev_tool_config)
    env: dict[str, str] = Field(default_factory=dict)

    @classmethod
    def settings_customise_sources(cls, settings_cls, **_):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Only load from `pyproject.toml`."""
        return (PyprojectTomlConfigSettingsSource(settings_cls),)
