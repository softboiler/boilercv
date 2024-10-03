"""Sync `dvc.yaml` and `params.yaml` with pipeline specification."""

from pathlib import Path

from cappa.base import command
from pydantic import BaseModel, Field


@command(default_long=True, invoke="boilercv_pipeline.sync_dvc.__main__.main")
class SyncDvc(BaseModel):
    """Sync `dvc.yaml` and `params.yaml` with pipeline specification."""

    pipeline: Path = Path("dvc.yaml")
    """Primary config file describing the DVC pipeline."""
    params: Path = Path("params.yaml")
    """DVC's primary parameters YAML file."""
    update_param_values: bool = Field(default=False)
    """Update values of parameters in the parameters YAML file."""
