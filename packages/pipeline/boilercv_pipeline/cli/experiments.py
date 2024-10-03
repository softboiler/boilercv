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
        run("boilercv_pipeline sync-dvc")
        run("dvc exp run --single-item --set-param stage=sample")


@command
class Trackpy(BaseModel):
    """Run TrackPy object finding experiment."""

    def __call__(self):
        """Run TrackPy object finding experiment."""
        run("dvc exp run --single-item --set-param stage=trackpy find_objects")


if __name__ == "__main__":
    invoke(Sample)
