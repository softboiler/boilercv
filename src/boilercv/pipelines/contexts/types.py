"""Types."""

from boilercv.contexts.types import (
    ContextPluginSettings,
    PluginConfigDict,
    SerializationInfo,
    ValidationInfo,
)
from boilercv.pipelines.contexts import PipelineCtxDict

PipelineConfigDict = PluginConfigDict[ContextPluginSettings[PipelineCtxDict]]
PipelineValidationInfo = ValidationInfo[PipelineCtxDict]
PipelineSerializationInfo = SerializationInfo[PipelineCtxDict]
