"""Types."""

from pathlib import Path
from typing import TYPE_CHECKING, Literal, TypeAlias

from boilercv.contexts.types import ContextPluginSettings, PluginConfigDict
from boilercv.serializers.types import (
    ContextFieldSerializationInfo,
    ContextSerializationInfo,
)
from boilercv.validators.types import ContextFieldValidationInfo, ContextValidationInfo

if TYPE_CHECKING:
    from boilercv_pipeline.models.contexts import BoilercvPipelineContext

BoilercvPipelineConfigDict: TypeAlias = PluginConfigDict[
    ContextPluginSettings["BoilercvPipelineContext"]
]
BoilercvPipelineValidationInfo: TypeAlias = ContextValidationInfo[
    "BoilercvPipelineContext"
]
BoilercvPipelineFieldValidationInfo: TypeAlias = ContextFieldValidationInfo[
    "BoilercvPipelineContext"
]
BoilercvPipelineSerializationInfo: TypeAlias = ContextSerializationInfo[
    "BoilercvPipelineContext"
]
BoilercvPipelineFieldSerializationInfo: TypeAlias = ContextFieldSerializationInfo[
    "BoilercvPipelineContext"
]
Kind: TypeAlias = Literal["DataDir", "DataFile", "DocsDir", "DocsFile"]
"""File or directory kind."""
Kinds: TypeAlias = dict[Path, Kind]
"""Paths and their kinds."""
