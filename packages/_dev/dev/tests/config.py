"""Settings."""

from pathlib import Path

from boilercore.settings_models import (
    customise_sources,
    get_settings_paths,
    sync_settings_schema,
)
from pydantic import BaseModel
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

from dev import tests


class Constants(BaseModel):
    """Constants."""

    data: Path = Path("docs") / "data"


const = Constants()
paths = get_settings_paths(tests)


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
        return customise_sources(settings_cls, init_settings, paths.plugin_settings)


class Settings(BaseSettings, use_attribute_docstrings=True):
    """Package settings."""

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        *_args: PydanticBaseSettingsSource,
        **_kwds: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Source  settings from init and TOML."""
        return customise_sources(settings_cls, init_settings, paths.settings)


for path, model in zip(
    paths.all_dev_settings if paths.in_dev else paths.all_cwd_settings,
    (PluginModelConfig, Settings),
    strict=True,
):
    sync_settings_schema(path, model)

default = Settings()
