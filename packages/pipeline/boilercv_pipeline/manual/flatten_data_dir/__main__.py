from itertools import chain
from pathlib import Path

from boilercv_pipeline.manual.flatten_data_dir import FlattenDataDir
from cappa.base import invoke


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


if __name__ == "__main__":
    invoke(FlattenDataDir)
