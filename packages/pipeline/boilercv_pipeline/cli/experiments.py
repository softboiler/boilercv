"""Run DVC experiments."""

from pathlib import Path
from shlex import split
from subprocess import run

from cappa import invoke
from cappa.base import command
from dev.tools import environment
from pydantic import BaseModel
from yaml import safe_dump, safe_load


@command
class Trackpy(BaseModel):
    """Run TrackPy object finding experiment."""

    def __call__(self):
        """Run TrackPy object finding experiment."""
        run(args=split("git checkout trackpy"), check=False)
        params_yaml = Path("params.yaml")
        params_yaml.write_text(
            encoding="utf-8",
            data=safe_dump(
                indent=2,
                sort_keys=False,
                width=float("inf"),
                data={
                    **safe_load(params_yaml.read_text(encoding="utf-8")),
                    "compare_with_trackpy": "--compare-with-trackpy",
                    "frame_count": 500,
                },
            ),
        )
        environment.run("pre-commit run --all-files prettier", check=False)
        for cmd in ["git add .", "git commit -m 'prepare for trackpy experiment'"]:
            run(args=split(cmd), check=False)
        environment.run("dvc repro find_objects", check=False)
        for cmd in [
            "git add .",
            "git commit -m 'repro trackpy experiment'",
            "git push",
        ]:
            run(args=split(cmd), check=False)


if __name__ == "__main__":
    invoke(Trackpy)
