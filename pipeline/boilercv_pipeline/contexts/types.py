"""Types."""

from typing import Any, Generic, Protocol, TypedDict, TypeVar

import pydantic
from pydantic import ConfigDict


class AnyTypedDict(TypedDict):
    """Base class representing any typed dictionary."""


class Contexts(AnyTypedDict):
    """Contexts."""


PluginSettings_T = TypeVar("PluginSettings_T", bound=AnyTypedDict, covariant=True)
"""Plugin settings type."""
Contexts_T = TypeVar("Contexts_T", bound=Contexts, covariant=True)
"""Contexts type."""


class PluginConfigDict(ConfigDict, Generic[PluginSettings_T]):
    """Plugin settings config dict."""

    plugin_settings: PluginSettings_T  # pyright: ignore[reportIncompatibleVariableOverride]


class ValidationInfo(pydantic.ValidationInfo, Protocol[Contexts_T]):
    """Pydantic validation info with a guaranteed context."""

    @property
    def context(self) -> Contexts_T | Any: ...  # noqa: D102


class ContextsPluginSettings(TypedDict, Generic[Contexts_T]):
    """Context model Pydantic plugin settings."""

    contexts: Contexts_T
