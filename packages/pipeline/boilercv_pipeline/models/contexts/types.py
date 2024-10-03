"""Types."""

from pathlib import Path
from typing import TYPE_CHECKING, Literal, TypeAlias

from context_models.serializers.types import ContextSerializationInfo
from context_models.types import ContextPluginSettings, PluginConfigDict
from context_models.validators.types import ContextValidationInfo

if TYPE_CHECKING:
    from boilercv_pipeline.models.contexts import BoilercvPipelineContexts

BoilercvPipelineConfigDict: TypeAlias = PluginConfigDict[
    ContextPluginSettings["BoilercvPipelineContexts"]
]
BoilercvPipelineValidationInfo: TypeAlias = ContextValidationInfo[
    "BoilercvPipelineContexts"
]
BoilercvPipelineSerializationInfo: TypeAlias = ContextSerializationInfo[
    "BoilercvPipelineContexts"
]
Kind: TypeAlias = Literal["DataDir", "DataFile", "DocsDir", "DocsFile"]
"""File or directory kind."""
Kinds: TypeAlias = dict[Path, Kind]
"""Paths and their kinds."""
