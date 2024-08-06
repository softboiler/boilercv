"""Settings."""

from boilercore.settings_models import (
    customise_sources,
    get_settings_paths,
    sync_settings_schema,
)
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

import boilercv_pipeline
from boilercv_pipeline.models import Params
from boilercv_pipeline.models.notebooks import Notebooks

settings_paths = get_settings_paths(boilercv_pipeline)


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
            settings_cls, init_settings, settings_paths.plugin_settings
        )


class Settings(BaseSettings):
    """Package settings."""

    model_config = SettingsConfigDict(use_attribute_docstrings=True)
    notebooks: Notebooks = Notebooks()

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

    @property
    def params(self):
        """All project parameters, including paths."""
        return Params()


for path, model in zip(
    settings_paths.all_dev_settings
    if settings_paths.in_dev
    else settings_paths.all_cwd_settings,
    (PluginModelConfig, Settings),
    strict=True,
):
    sync_settings_schema(path, model)


default = Settings()
