"""Project parameters."""

from pathlib import Path

from boilercore.fits import Fit
from boilercore.models import SynchronizedPathsYamlModel
from pydantic import Field

from boilercv_pipeline import PROJECT_PATH
from boilercv_pipeline.models.paths import Paths


class Params(SynchronizedPathsYamlModel):
    """Project parameters."""

    paths: Paths
    fit: Fit = Field(default_factory=Fit, description="Parameters for model fit.")

    def __init__(
        self, data_file: Path = Path("params.yaml"), root: Path = PROJECT_PATH
    ):
        super().__init__(data_file, paths=Paths(root=root.resolve()))


PARAMS = Params()
"""All project parameters, including paths."""
