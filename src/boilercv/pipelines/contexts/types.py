"""Types."""

from typing import TYPE_CHECKING, TypeAlias

from context_models.types import (
    ContextPluginSettings,
    PluginConfigDict,
    SerializationInfo,
    ValidationInfo,
)

if TYPE_CHECKING:
    from boilercv.pipelines.contexts import PipelineContext, PipelineCtxDict

from boilercv.pipelines.pipes import ContextValue

PipelineConfigDict: TypeAlias = PluginConfigDict[
    "ContextPluginSettings[PipelineCtxDict]"
]
PipelineValidationInfo: TypeAlias = "ValidationInfo[PipelineCtxDict]"
PipelineSerializationInfo: TypeAlias = "SerializationInfo[PipelineCtxDict]"
PipelineContextLike: TypeAlias = "PipelineContext | ContextValue"
