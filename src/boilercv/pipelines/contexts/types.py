"""Types."""

from typing import TypeAlias

from boilercv.contexts.types import (
    ContextPluginSettings,
    PluginConfigDict,
    SerializationInfo,
    ValidationInfo,
)
from boilercv.pipelines.contexts import PipelineCtxDict

PipelineConfigDict: TypeAlias = PluginConfigDict[ContextPluginSettings[PipelineCtxDict]]
PipelineValidationInfo: TypeAlias = ValidationInfo[PipelineCtxDict]
PipelineSerializationInfo: TypeAlias = SerializationInfo[PipelineCtxDict]