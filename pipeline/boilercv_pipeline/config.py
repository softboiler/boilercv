"""Settings."""

from pathlib import Path

from boilercore.paths import get_package_dir, map_stages
from pydantic import BaseModel

import boilercv_pipeline


class Constants(BaseModel, use_attribute_docstrings=True):
    """Constants."""

    package_dir: Path = get_package_dir(boilercv_pipeline)
    """Package directory."""
    stages: dict[str, Path] = {
        k: v
        for k, v in map_stages(package_dir / "stages").items()
        if not k.startswith("common_")
    }
    """Stages."""
    data: Path = Path("data")
    docs: Path = Path("docs")


const = Constants()
"""Constants."""
