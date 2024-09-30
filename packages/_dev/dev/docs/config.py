"""Configuration."""

from boilercore.settings_models import (
    customise_sources,
    get_settings_paths,
    sync_settings_schema,
)
from pydantic import Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

from dev import docs
from dev.docs.models import Build

settings_paths = get_settings_paths(docs)


class PluginModelConfig(BaseSettings, use_attribute_docstrings=True):
    """Pydantic plugin model configuration."""

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
            settings_cls, init_settings, settings_paths.plugin_settings
        )


class Settings(BaseSettings, use_attribute_docstrings=True):
    """Package settings."""

    build: Build = Field(default_factory=Build)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        *_args: PydanticBaseSettingsSource,
        **_kwds: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Source  settings from init and TOML."""
        return customise_sources(settings_cls, init_settings, settings_paths.settings)


for path, model in zip(
    settings_paths.all_dev_settings
    if settings_paths.in_dev
    else settings_paths.all_cwd_settings,
    (PluginModelConfig, Settings),
    strict=True,
):
    sync_settings_schema(path, model)

default = Settings()
