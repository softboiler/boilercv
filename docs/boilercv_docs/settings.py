"""Settings."""

from collections.abc import Iterable
from itertools import chain
from json import dumps
from pathlib import Path
from shutil import rmtree
from site import getsitepackages
from typing import Annotated

from boilercore.paths import get_module_name, get_package_dir
from pydantic import AfterValidator, BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

import boilercv_docs
from boilercv_docs import get_root


class Constants(BaseModel):
    """Constants."""

    encoding: str = "utf-8"

    package_dir: Path = get_package_dir(boilercv_docs)
    package_name: str = get_module_name(boilercv_docs)

    cwd_plugin_settings: Path = Path.cwd() / f"{package_name}_plugin.yaml"
    dev_plugin_settings: Path = package_dir / "settings_plugin.yaml"
    plugin_settings: list[Path] = [cwd_plugin_settings, dev_plugin_settings]

    cwd_settings: Path = Path.cwd() / Path(f"{package_name}.yaml")
    dev_settings: Path = package_dir / "settings.yaml"
    settings: list[Path] = [cwd_settings, dev_settings]

    all_cwd_settings: list[Path] = [cwd_plugin_settings, cwd_settings]
    all_dev_settings: list[Path] = [dev_plugin_settings, dev_settings]

    in_dev: bool = not (
        getsitepackages() and package_dir.is_relative_to(Path(getsitepackages()[0]))
    )


const = Constants()


def get_toml_sources(
    settings_cls: type[BaseSettings], paths: Iterable[Path]
) -> tuple[YamlConfigSettingsSource, ...]:
    """Source settings from init and TOML."""
    sources: list[YamlConfigSettingsSource] = []
    for yaml_file in paths:
        source = YamlConfigSettingsSource(
            settings_cls, yaml_file, yaml_file_encoding=const.encoding
        )
        if source.init_kwargs.get("$schema"):
            del source.init_kwargs["$schema"]
        sources.append(source)
    return tuple(sources)


class PluginModelConfig(BaseSettings):
    """Pydantic plugin model configuration."""

    model_config = SettingsConfigDict(use_attribute_docstrings=True)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        *_args: PydanticBaseSettingsSource,
        **_kwds: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Source settings from init and TOML."""
        return (init_settings, *get_toml_sources(settings_cls, const.plugin_settings))


def get_plugin_settings(config: PluginModelConfig) -> dict[str, PluginModelConfig]:
    """Get Pydantic plugin model configuration.

    ```Python
    model_config = SettingsConfigDict(
        plugin_settings={"boilercv_docs": PluginModelConfig()}
    )
    ```
    """
    return {const.package_name: config}


def remove_stale_autodoc(skip_autodoc: bool) -> bool:
    """Remove stale autodoc products."""
    if skip_autodoc:
        rmtree(get_root() / "docs" / "apidocs", ignore_errors=True)
    return skip_autodoc


class Settings(BaseSettings):
    """Package settings."""

    model_config = SettingsConfigDict(use_attribute_docstrings=True)

    force_dev: bool = False
    """Force building documentation with dev-only data tracked by DVC."""
    nb_execution_excludepatterns: Annotated[
        list[str],
        AfterValidator(
            lambda patterns: [
                p.resolve().as_posix()
                for p in chain.from_iterable([
                    Path.cwd().glob(f"{pat}/**/*.ipynb") for pat in patterns
                ])
            ]
        ),
    ] = Field(default_factory=list)
    """List of directories relative to `docs` to exclude executing notebooks in."""
    skip_autodoc: Annotated[bool, AfterValidator(remove_stale_autodoc)] = False
    """Skip the potentially slow process of autodoc generation."""

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        *_args: PydanticBaseSettingsSource,
        **_kwds: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Source settings from init and TOML."""
        return (init_settings, *get_toml_sources(settings_cls, const.settings))


def sync_settings_schema(path: Path, model: type[BaseModel]) -> None:
    """Create files and update schemas."""
    if not path.exists():
        path.touch()
    schema = path.with_name(f"{path.stem}_schema.json")
    schema.write_text(
        encoding=const.encoding, data=f"{dumps(model.model_json_schema(), indent=2)}\n"
    )


for path, model in zip(
    const.all_dev_settings if const.in_dev else const.all_cwd_settings,
    (PluginModelConfig, Settings),
    strict=True,
):
    sync_settings_schema(path, model)

default = Settings()
