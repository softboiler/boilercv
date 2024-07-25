"""Project parameters."""

from pathlib import Path

from boilercore.models import SynchronizedPathsYamlModel
from pydantic import Field

from boilercv_pipeline import PROJECT_PATH
from boilercv_pipeline.models.paths import Paths
from boilercv_pipeline.types import Slicer2D


class Params(SynchronizedPathsYamlModel):
    """Project parameters."""

    paths: Paths = Field(default_factory=Paths)
    cine_crops: dict[str, Slicer2D] = Field(
        default={r"Y20240718.+": ((59, None), (None, None))}
    )

    def __init__(self, data_file: Path = PROJECT_PATH / "params.yaml", **kwargs):
        """Initialize, propagate paths to the parameters file, and update the schema."""
        super().__init__(data_file, **kwargs)


PARAMS = Params()
"""All project parameters, including paths."""
