"""Types."""

from boilercv.contexts.types import (
    ContextPluginSettings,
    PluginConfigDict,
    SerializationInfo,
    ValidationInfo,
)
from boilercv.morphs.contexts import PipelineCtxDict

PipelineConfigDict = PluginConfigDict[ContextPluginSettings[PipelineCtxDict]]
PipelineValidationInfo = ValidationInfo[PipelineCtxDict]
PipelineSerializationInfo = SerializationInfo[PipelineCtxDict]
