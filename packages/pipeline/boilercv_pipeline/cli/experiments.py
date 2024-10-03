"""Run DVC experiments."""

from pathlib import Path

from cappa import invoke
from cappa.base import command
from dev.tools.environment import run
from dvc.utils.hydra import compose_and_dump
from pydantic import BaseModel


@command
class Sample(BaseModel):
    """Run sample experiment."""

    def __call__(self):
        """Run experiment with just the sample video."""
        compose_and_dump(
            output_file=Path("params.yaml"),
            config_dir=Path("conf").resolve().as_posix(),
            config_module=None,
            config_name="config",
            plugins_path="hydra_plugins",
            overrides=["stage=sample"],
        )
        run("boilercv_pipeline sync-dvc", check=False)
        run("dvc exp remove sample", check=False)
        run("dvc exp run --name sample --set-param stage=sample", check=False)


@command
class Trackpy(BaseModel):
    """Run TrackPy object finding experiment."""

    def __call__(self):
        """Run TrackPy object finding experiment."""
        run(
            "dvc exp run --single-item --set-param stage=trackpy find_objects",
            check=False,
        )


if __name__ == "__main__":
    invoke(Sample)
