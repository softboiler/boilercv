"""Run DVC experiments."""

from cappa import invoke
from cappa.base import command
from dev.tools.environment import run
from pydantic import BaseModel


@command
class Sample(BaseModel):
    """Run TrackPy object finding experiment."""

    def __call__(self):
        """Run experiment with just the sample video."""
        run("dvc exp run --queue --name sample --set-param stage=sample")
        run("dvc exp apply sample")
        run("boilercv_pipeline sync-dvc")
        run("dvc exp remove sample")
        run("dvc exp run --name sample --set-param stage=sample")


@command
class Trackpy(BaseModel):
    """Run TrackPy object finding experiment."""

    def __call__(self):
        """Run TrackPy object finding experiment."""
        run("dvc exp run --single-item --set-param stage=trackpy find_objects")


if __name__ == "__main__":
    invoke(Sample)
