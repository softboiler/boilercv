"""Project parameters."""

from pathlib import Path
from typing import ClassVar

from boilercore.fits import Fit
from boilercore.models import SynchronizedPathsYamlModel
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from boilercv_pipeline import PROJECT_PATH
from boilercv_pipeline.models.paths import Paths


class Params(SynchronizedPathsYamlModel, BaseSettings):
    """Project parameters."""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(  # pyright: ignore[reportIncompatibleVariableOverride]
        env_prefix="BOILERCV_", env_nested_delimiter="__"
    )

    paths: Paths
    fit: Fit = Field(default_factory=Fit, description="Parameters for model fit.")

    def __init__(self, root: Path | None = None, data_file: Path | None = None):
        root = (root or Path.cwd()).resolve()
        data_file = data_file or root / "params.yaml"
        super().__init__(data_file, paths=Paths(root=root))


PARAMS = Params(root=PROJECT_PATH)
"""All project parameters, including paths."""
