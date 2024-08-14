"""Types."""

from pathlib import Path
from typing import TypeAlias, TypedDict

from boilercv_pipeline.contexts.types import (
    Contexts,
    ContextsPluginSettings,
    CtxValidationInfo,
    PluginConfigDict,
)


class RootCtx(TypedDict):
    """Root directory contexts."""

    data: Path
    docs: Path


class RootContexts(Contexts):
    """Root directory contexts."""

    root: RootCtx


RootContextsValidationInfo: TypeAlias = CtxValidationInfo[RootContexts]
RootSettings: TypeAlias = ContextsPluginSettings[RootContexts]
RootConfigDict: TypeAlias = PluginConfigDict[RootSettings]
