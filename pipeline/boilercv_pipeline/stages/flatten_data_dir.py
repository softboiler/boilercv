"""Flatten the data directory structure.

Directory structure looks like

    data
    └───YYYY-MM-DD
        ├───data
        ├───notes
        └───video
"""

from __future__ import annotations

from itertools import chain
from pathlib import Path
from typing import Annotated

from boilercore.models import DefaultPathsModel
from cappa.arg import Arg
from cappa.base import command, invoke
from pydantic import BaseModel, Field

from boilercv_pipeline.models import get_parser
from boilercv_pipeline.models.config import default


class Deps(DefaultPathsModel):
    root: Path = Field(default=default.paths.root, exclude=True)
    stage: Path = Path(__file__)
    hierarchical_data: Path = default.paths.hierarchical_data
    notes: Path = default.paths.notes
    cines: Path = default.paths.cines
    sheets: Path = default.paths.sheets


class Outs(DefaultPathsModel):
    root: Path = Field(default=default.paths.root, exclude=True)
    notes: Path = default.paths.notes
    cines: Path = default.paths.cines
    sheets: Path = default.paths.sheets


def main(args: FlattenDataDir):
    source = args.deps.hierarchical_data
    rename_notes(source, args.outs.notes)
    rename_cines(source, args.outs.cines)
    rename_sheets(source, args.outs.sheets)


def rename_notes(source: Path, notes: Path):
    """Rename nested notes."""
    for trial, note in {
        trial.stem: trial / "notes"
        for trial in sorted(source.iterdir())
        if trial.is_dir()
    }.items():
        if not note.exists():
            continue
        note.rename(notes / trial)


def rename_cines(source: Path, cines: Path):
    """Rename nested cines."""
    trials = [trial / "video" for trial in source.iterdir() if trial.is_dir()]
    for video in sorted(chain.from_iterable(trial.glob("*.cine") for trial in trials)):
        video.rename(cines / video.name.removeprefix("results_"))


def rename_sheets(source: Path, sheets: Path):
    """Rename nested sheets."""
    data = [trial / "data" for trial in sorted(source.iterdir()) if trial.is_dir()]
    for sheet in sorted(chain.from_iterable(trial.glob("*.csv") for trial in data)):
        sheet.rename(sheets / sheet.name.removeprefix("results_"))


@command(invoke=main, default_long=True)
class FlattenDataDir(BaseModel):
    deps: Annotated[Deps, Arg(parse=get_parser(Deps), hidden=True)] = Deps()
    outs: Annotated[Outs, Arg(parse=get_parser(Deps), hidden=True)] = Outs()


if __name__ == "__main__":
    invoke(FlattenDataDir)
