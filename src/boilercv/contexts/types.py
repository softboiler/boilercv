"""Types."""

from collections.abc import MutableMapping
from typing import Any, Generic, Protocol, TypeAlias, TypeVar

import pydantic
from pydantic import BaseModel, ConfigDict
from typing_extensions import TypedDict

Data: TypeAlias = BaseModel | MutableMapping[str, Any]
"""Data."""


class AnyTypedDict(TypedDict):
    """Base class representing any typed dictionary."""


class Context(AnyTypedDict):
    """Context."""


K = TypeVar("K")
"""Key type."""
V = TypeVar("V")
"""Value type."""
PluginSettings_T = TypeVar(
    "PluginSettings_T", bound=BaseModel | AnyTypedDict, covariant=True
)
"""Plugin settings type."""
Context_T = TypeVar("Context_T", bound=Context, covariant=True)
"""Context type."""
Data_T = TypeVar("Data_T", bound=Data)
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


class FieldSerializationInfo(pydantic.FieldSerializationInfo, Protocol[Context_T]):
    """Pydantic validation info with a guaranteed context."""

    @property
    def context(self) -> Context_T | Any: ...  # noqa: D102


class ContextPluginSettings(TypedDict, Generic[Context_T]):
    """Context model Pydantic plugin settings."""

    context: Context_T


Config: TypeAlias = PluginConfigDict[ContextPluginSettings[Context]]
PluginSettings: TypeAlias = ContextPluginSettings[Context]
ContextTree: TypeAlias = dict[str, "ContextNode"]
"""Context tree."""


class ContextNode(TypedDict):
    """Context tree."""

    config: Config
    plugins: PluginSettings
    context: Context
    context_tree: ContextTree
