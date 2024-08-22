"""Types."""

from typing import Any, Generic, Protocol, TypeVar

import pydantic
from pydantic import BaseModel, ConfigDict
from typing_extensions import TypedDict


class AnyTypedDict(TypedDict):
    """Base class representing any typed dictionary."""


class Context(AnyTypedDict):
    """Context."""


PluginSettings_T = TypeVar("PluginSettings_T", bound=AnyTypedDict, covariant=True)
"""Plugin settings type."""
Context_T = TypeVar("Context_T", bound=Context, covariant=True)
"""Context type."""
Data_T = TypeVar("Data_T", bound=BaseModel | dict[str, Any])
"""Data type."""


class PluginConfigDict(ConfigDict, Generic[PluginSettings_T]):
    """Plugin settings config dict."""

    plugin_settings: PluginSettings_T  # pyright: ignore[reportIncompatibleVariableOverride]


class ValidationInfo(pydantic.ValidationInfo, Protocol[Context_T]):
    """Pydantic validation info with a guaranteed context."""

    @property
    def context(self) -> Context_T | Any: ...  # noqa: D102


class SerializationInfo(pydantic.SerializationInfo, Protocol[Context_T]):
    """Pydantic validation info with a guaranteed context."""

    @property
    def context(self) -> Context_T | Any: ...  # noqa: D102


class ContextPluginSettings(TypedDict, Generic[Context_T]):
    """Context model Pydantic plugin settings."""

    context: Context_T
