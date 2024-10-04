"""Run DVC experiments."""

from collections.abc import Iterable
from pathlib import Path

from cappa.base import command, invoke
from dev.tools.environment import run
from dvc.utils.hydra import compose_and_dump
from pydantic import BaseModel

from boilercv_pipeline.sync_dvc import SyncDvc

# TODO: Implement sweeps
# dvc.utils.hydra.get_hydra_sweeps({"params.yaml": {"stage.scale=choice(1.0, 1.3)"}})


class Forceable(BaseModel):
    """Forceable model."""

    force: bool = False


@command
class Sample(Forceable):
    """Run sample experiment."""

    def __call__(self):
        """Run experiment with just the sample video."""
        run_experiment(
            exp="sample", stages=("find_objects", "find_tracks"), force=self.force
        )


@command
class Trackpy(Forceable):
    """Run TrackPy object finding experiment."""

    def __call__(self):
        """Run TrackPy object finding experiment."""
        run_experiment(exp="trackpy", stages="find_objects", force=self.force)


def run_experiment(
    exp: str = "",
    stages: Iterable[str] | None = None,
    params: Path = Path("params.yaml"),
    force: bool = False,
):
    """Run experiment."""
    compose_and_dump(
        output_file=Path(params),
        config_dir=Path("conf").resolve().as_posix(),
        config_module=None,
        config_name="config",
        plugins_path="hydra_plugins",
        overrides=[f"stage={exp}"] if exp else [],
    )
    sep = " "
    invoke(SyncDvc)
    if exp and force:
        run(f"dvc exp remove {exp}", check=False, capture_output=True)
    run(
        sep.join([
            "dvc exp run",
            *([f"--name {exp} --set-param stage={exp}"] if exp else []),
            *([f"--single-item {sep.join(tuple(stages))}"] if stages else []),
        ])
    )


if __name__ == "__main__":
    invoke(Sample, argv=["--force"])
