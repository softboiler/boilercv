"""Project parameters."""

from boilercore.fits import Fit
from boilercore.models import SynchronizedPathsYamlModel
from pydantic import Field, FilePath

from boilercv_pipeline import PROJECT_PATH
from boilercv_pipeline.models.paths import PackagePaths, Paths


class Params(SynchronizedPathsYamlModel):
    """Project parameters."""

    source: FilePath = PROJECT_PATH / "params.yaml"
    paths: Paths = Field(default_factory=Paths)
    package_paths: PackagePaths = Field(default_factory=PackagePaths)
    fit: Fit = Field(default_factory=Fit, description="Parameters for model fit.")


PARAMS = Params()
"""All project parameters, including paths."""
