"""Types."""

from pathlib import Path
from typing import TYPE_CHECKING, Literal, TypeAlias

from boilercv.contexts.types import (
    ContextPluginSettings,
    FieldSerializationInfo,
    PluginConfigDict,
    SerializationInfo,
    ValidationInfo,
)

if TYPE_CHECKING:
    from boilercv_pipeline.models.contexts import BoilercvPipelineCtxDict

BoilercvPipelineConfigDict: TypeAlias = PluginConfigDict[
    ContextPluginSettings["BoilercvPipelineCtxDict"]
]
BoilercvPipelineValidationInfo: TypeAlias = ValidationInfo["BoilercvPipelineCtxDict"]
BoilercvPipelineSerializationInfo: TypeAlias = SerializationInfo[
    "BoilercvPipelineCtxDict"
]
BoilercvPipelineFieldSerializationInfo: TypeAlias = FieldSerializationInfo[
    "BoilercvPipelineCtxDict"
]
Kind: TypeAlias = Literal["DataDir", "DataFile", "DocsDir", "DocsFile"]
"""File or directory kind."""
Kinds: TypeAlias = dict[Path, Kind]
"""Paths and their kinds."""
