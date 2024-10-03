"""Output data model."""

from typing import Generic

from context_models.validators import context_field_validator
from matplotlib.figure import Figure
from pandas import DataFrame
from pydantic import BaseModel, Field

from boilercv_pipeline.models.contexts.types import BoilercvPipelineValidationInfo
from boilercv_pipeline.models.data.types import Dfs_T, Plots_T
from boilercv_pipeline.models.path import (
    BoilercvPipelineContextStore,
    get_boilercv_pipeline_config,
)
from boilercv_pipeline.sync_dvc.validators import dvc_append_plot_name


class Dfs(BaseModel, arbitrary_types_allowed=True):
    """Data frames."""

    src: DataFrame = Field(default_factory=DataFrame)
    """Source data for this stage."""
    dst: DataFrame = Field(default_factory=DataFrame)
    """Destination data for this stage."""


class Plots(BoilercvPipelineContextStore, arbitrary_types_allowed=True):
    """Plots."""

    model_config = get_boilercv_pipeline_config()

    @context_field_validator("*", mode="after")
    @classmethod
    def dvc_validate_plot(
        cls, figure: Figure, info: BoilercvPipelineValidationInfo
    ) -> Figure:
        """Append plot name for `dvc.yaml`."""
        return dvc_append_plot_name(figure, info)


class Data(BoilercvPipelineContextStore, Generic[Dfs_T, Plots_T]):
    """Data frame and plot outputs."""

    model_config = get_boilercv_pipeline_config()

    dfs: Dfs_T = Field(default_factory=Dfs)
    plots: Plots_T = Field(default_factory=Plots)
