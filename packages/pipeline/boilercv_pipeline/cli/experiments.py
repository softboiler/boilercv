"""Run DVC experiments."""

from pathlib import Path

from cappa import invoke
from cappa.base import command
from dev.tools.environment import run
from dvclive import Live
from pydantic import BaseModel
from yaml import safe_dump, safe_load


@command
class Trackpy(BaseModel):
    """Run TrackPy object finding experiment."""

    def __call__(self):
        """Run TrackPy object finding experiment."""
        dvc_yaml = Path("dvc.yaml")
        dvc_yaml.write_text(
            encoding="utf-8",
            data=safe_dump(
                sort_keys=False,
                indent=2,
                width=float("inf"),
                data={
                    "stages": {
                        stage: value
                        for stage, value in safe_load(
                            dvc_yaml.read_text(encoding="utf-8")
                        )["stages"].items()
                        if stage == "find_objects"
                    }
                },
            ),
        )
        params_yaml = Path("params.yaml")
        params_yaml.write_text(
            encoding="utf-8",
            data=safe_dump(
                sort_keys=False,
                indent=2,
                width=float("inf"),
                data={
                    **safe_load(params_yaml.read_text(encoding="utf-8")),
                    "compare_with_trackpy": "--compare-with-trackpy",
                    "frame_count": 500,
                    "only_sample": "--only-sample",
                },
            ),
        )
        run("pre-commit run --all-files prettier", check=False)
        with Live(".", resume=True):
            pass


if __name__ == "__main__":
    invoke(Trackpy)
