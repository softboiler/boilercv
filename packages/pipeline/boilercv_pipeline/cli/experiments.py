"""Run DVC experiments."""

from cappa.base import command
from dvclive import Live
from pydantic import BaseModel


@command
class Trackpy(BaseModel):
    """Run TrackPy object finding experiment."""

    def __call__(self):
        """Run TrackPy object finding experiment."""
        with Live() as live:
            live.log_params({
                "frame_count": 1500,
                "compare_with_trackpy": "--compare-with-trackpy",
            })
