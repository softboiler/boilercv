"""Generate equation documentation."""

from asyncio import TaskGroup, run
from pathlib import Path
from sys import stdout
from textwrap import dedent
from tomllib import loads
from typing import cast, get_args

from cyclopts import App
from loguru import logger
from watchfiles import awatch

from boilercv.correlations import GROUPS
from boilercv.correlations.models import Equations, prep_equation_forms
from boilercv.correlations.types import Corr, Kind, Range
from boilercv_pipeline.equations import EQUATIONS, SYMS, get_raw_equations_context

logger.remove()
logger.add(sink=stdout, format="<level>{message}</level>")

DIR_TO_WATCH = Path("src") / "boilercv" / "correlations"
"""Directory to watch."""
FILTER = [*DIR_TO_WATCH.rglob("equations.toml"), *DIR_TO_WATCH.rglob("ranges.toml")]
"""Files in directory to watch."""

INTERVAL = 5
"""Seconds to wait before checking again."""
COOLDOWN = 2
"""Wait at least this many seconds before triggering `on_modified` again."""

OUT = Path("docs") / "experiments" / "e230920_subcool" / "correlations" / "equations.md"
"""Generated equations directory."""
APP = App()
"""CLI."""

SEP = " "
"""Line separator."""


async def main():  # noqa: D103
    logger.info("Generating docs.")
    make_docs()
    logger.success("Generated docs.")
    async with TaskGroup() as tg:
        for corr in (*get_args(Corr), *get_args(Range)):
            tg.create_task(watch_eqs(corr))


async def watch_eqs(corr: Corr | Range):
    """Watch for changes in equations."""
    async for changes in awatch(DIR_TO_WATCH / ("" if corr == "range" else corr)):
        for _change, path in [
            (c[0], Path(c[1]).relative_to(Path.cwd())) for c in changes
        ]:
            if path not in FILTER:
                logger.warning(
                    SEP.join([
                        f"Modified file '{path.name}' not in filter.",
                        "Not regenerating docs.",
                    ])
                )
                continue
            logger.warning("Equation modification detected. Regenerating docs.")
            make_docs()
            logger.success("Regenerated docs.")


def make_docs():
    """Generate equation documentation."""
    all_eqs: dict[Corr, Equations[str]] = {
        corr: get_equations(corr) for corr in get_args(Corr)
    }
    all_ranges = get_equations("range")
    header = "# Correlation equations\n"
    groups = ""
    for group in ["Group 1", "Group 3", "Group 4", "Group 5"]:
        groups += f"\n## {group}\n"
        for name in all_eqs["beta"]:
            if GROUPS[name] == group:
                eqs = {
                    **{
                        corr: prep_equation_forms(
                            cast(dict[Kind, str], all_eqs[corr][name])
                        )["latex"]
                        for corr in get_args(Corr)
                    },
                    "range": prep_equation_forms(
                        cast(dict[Kind, str], all_ranges[name])
                    )["latex"],
                }
                latex_eqs = "".join([
                    f"""
                    $$
                    {eq}
                    $$ (eq_{corr}_{name})
                    """
                    for corr, eq in eqs.items()
                    if eq
                ])
                groups += dedent(f"""
                    ### {name}
                    {latex_eqs}""")
    OUT.write_text(encoding="utf-8", data=f"{header}\n{groups.strip()}\n")


def get_equations(corr: Corr | Range) -> Equations[str]:
    """Get equations."""
    equations = (
        Equations[str]
        .context_model_validate(
            obj=loads(
                EQUATIONS[corr].read_text("utf-8") if EQUATIONS[corr].exists() else ""
            ),
            context=get_raw_equations_context(symbols=SYMS),
        )
        .model_dump()
    )

    return equations


if __name__ == "__main__":
    run(main())
