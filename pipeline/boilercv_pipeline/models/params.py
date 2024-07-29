"""Project parameters."""

from pathlib import Path

from boilercore.fits import Fit
from boilercore.models import SynchronizedPathsYamlModel
from pydantic import Field

from boilercv_pipeline import PROJECT_PATH
from boilercv_pipeline.models.paths import Paths


class Params(SynchronizedPathsYamlModel):
    """Project parameters."""

    paths: Paths = Field(default_factory=Paths)
    fit: Fit = Field(default_factory=Fit, description="Parameters for model fit.")

    def __init__(self, data_file: Path = PROJECT_PATH / "params.yaml", **kwargs):
        """Initialize, propagate paths to the parameters file, and update the schema."""
        super().__init__(data_file, **kwargs)


PARAMS = Params()
"""All project parameters, including paths."""
