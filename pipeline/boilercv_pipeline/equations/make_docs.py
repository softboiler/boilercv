"""Generate equation documentation."""

from asyncio import TaskGroup, run
from pathlib import Path
from sys import stdout
from tomllib import loads
from typing import get_args

from cyclopts import App
from loguru import logger
from watchfiles import awatch

from boilercv.correlations import GROUPS, META_TOML, RANGES_TOML, get_equations
from boilercv.correlations.models import Equations, Metadata
from boilercv.correlations.types import Corr, Equation, Range
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
    all_eqs = {corr: get_raw_equations(corr) for corr in get_args(Corr)}
    ranges = {name: r.latex for name, r in get_equations(RANGES_TOML).items()}
    meta = Metadata.context_model_validate(
        obj=loads(META_TOML.read_text("utf-8") if META_TOML.exists() else ""),
        context=Metadata.get_context(),
    )
    header = "# Correlation equations\n"
    groups = ""
    for group in ["Group 1", "Group 3", "Group 4", "Group 5"]:
        groups += f"\n## {group}\n"
        for name in get_args(Equation):
            if GROUPS[name] == group:
                latex = f"""
$$
{all_eqs["nusselt"][name]}
$$ (eq_nusselt_{name})

$$
{all_eqs["beta"][name]}
$$ (eq_beta_{name})
"""
                latex += (
                    f"""
$$
{ranges[name]}
$$ (eq_range_{name})
"""
                    if ranges[name]
                    else ""
                )
                long_name = meta[name].name
                citekey = meta[name].citekey
                groups += f"""
### {long_name} {{cite}}`{citekey},tangReviewDirectContact2022`
{latex}"""
    OUT.write_text(encoding="utf-8", data=f"{header}\n{groups.strip()}\n")


def get_raw_equations(corr: Corr | Range) -> dict[Equation, str]:
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
    return {name: eq["latex"] for name, eq in equations.items()}


if __name__ == "__main__":
    run(main())
