"""Settings."""

from pathlib import Path

from boilercore.paths import get_package_dir, map_stages
from boilercore.settings_models import (
    Paths,
    customise_sources,
    get_settings_paths,
    sync_settings_schema,
)
from pydantic import BaseModel, ConfigDict
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

import boilercv_pipeline


class Constants(BaseModel):
    """Constants."""

    model_config = ConfigDict(use_attribute_docstrings=True)
    settings_paths: Paths = get_settings_paths(boilercv_pipeline)
    """Settings paths."""
    package_dir: Path = get_package_dir(boilercv_pipeline)
    """Package directory."""
    stages: dict[str, Path] = {
        k: v
        for k, v in map_stages(package_dir / "stages").items()
        if not k.startswith("common_")
    }
    """Stages."""


const = Constants()
"""Constants."""


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
        return customise_sources(
            settings_cls, init_settings, const.settings_paths.plugin_settings
        )


class Settings(BaseSettings):
    """Package settings."""

    model_config = SettingsConfigDict(use_attribute_docstrings=True)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        *_args: PydanticBaseSettingsSource,
        **_kwds: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Source  settings from init and TOML."""
        return customise_sources(
            settings_cls, init_settings, const.settings_paths.settings
        )


for path, model in zip(
    const.settings_paths.all_dev_settings
    if const.settings_paths.in_dev
    else const.settings_paths.all_cwd_settings,
    (PluginModelConfig, Settings),
    strict=True,
):
    sync_settings_schema(path, model)


default = Settings()