"""Types."""

from typing import Any, Generic, Protocol, TypedDict, TypeVar

import pydantic
from pydantic import ConfigDict


class AnyTypedDict(TypedDict):
    """Base class representing any typed dictionary."""


class Context(AnyTypedDict):
    """Context."""


PluginSettings_T = TypeVar("PluginSettings_T", bound=AnyTypedDict, covariant=True)
"""Plugin settings type."""
Context_T = TypeVar("Context_T", bound=Context, covariant=True)
"""Context type."""


class PluginConfigDict(ConfigDict, Generic[PluginSettings_T]):
    """Plugin settings config dict."""

    plugin_settings: PluginSettings_T  # pyright: ignore[reportIncompatibleVariableOverride]


class ValidationInfo(pydantic.ValidationInfo, Protocol[Context_T]):
    """Pydantic validation info with a guaranteed context."""

    @property
    def context(self) -> Context_T | Any: ...  # noqa: D102


class ContextPluginSettings(TypedDict, Generic[Context_T]):
    """Context model Pydantic plugin settings."""

    context: Context_T
