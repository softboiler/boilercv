"""Settings."""

from pathlib import Path

from boilercore.paths import get_package_dir, map_stages
from pydantic import BaseModel

import boilercv_pipeline


def get_root(
    pyproject: Path = Path("pyproject.toml"), docs: Path = Path("docs")
) -> Path:
    """Look for project root directory starting from current working directory."""
    cwd = Path().cwd()
    path = Path().cwd()
    while (path / "conf.py").exists() or not all(
        (path / check).exists() for check in [pyproject, docs]
    ):
        if path == (path := path.parent):
            return cwd
    return path


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
    # TODO: Don't rely on this heuristic for finding the root
    # ..... softboiler/boilercv#251
    root: Path = get_root()
    """Root directory."""
    data: Path = Path("data")
    """Data directory."""
    docs: Path = Path("docs")
    """Docs directory."""
    generated_stages: Path = (
        package_dir / "models" / "generated" / "types" / "stages.py"
    )
    """Generated stages."""


const = Constants()
"""Constants."""
