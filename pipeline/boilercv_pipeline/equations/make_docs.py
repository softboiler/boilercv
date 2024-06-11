"""Generate equation documentation."""

from pathlib import Path
from sys import stdout
from textwrap import dedent
from tomllib import loads

from cyclopts import App
from loguru import logger
from watchfiles import watch

from boilercv.correlations import GROUPS
from boilercv.correlations.models import Equations, prep_equation_forms
from boilercv.correlations.types import Corr
from boilercv_pipeline.equations import EQUATIONS, SYMS, get_raw_equations_context

logger.remove()
logger.add(sink=stdout, format="<level>{message}</level>")

DIR_TO_WATCH = Path("src") / "boilercv" / "correlations"
"""Directory to watch."""
FILTER = list(DIR_TO_WATCH.rglob("equations.toml"))
"""Files in directory to watch."""

INTERVAL = 5
"""Seconds to wait before checking again."""
COOLDOWN = 2
"""Wait at least this many seconds before triggering `on_modified` again."""

OUT = Path("docs") / "experiments" / "e230920_subcool" / "correlations"
"""Generated equations directory."""
APP = App()
"""CLI."""

SEP = " "
"""Line separator."""


def main():  # noqa: D103
    APP()


@APP.default
def default(corr: Corr = "beta"):  # noqa: D103
    logger.info(f"Generating {corr} docs.")
    make_docs(corr)
    logger.success(f"Generated {corr} docs.")
    for changes in watch(DIR_TO_WATCH / (corr)):
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
            logger.warning(f"Equation modification detected. Regenerating {corr} docs.")
            make_docs(corr)
            logger.success(f"Regenerated {corr} docs.")


def make_docs(corr: Corr):
    """Generate equation documentation."""
    equations_path = EQUATIONS[corr]
    content: str = (
        f"# {'Dimensionless bubble diameter' if corr == 'beta' else 'Nusselt number'}\n"
    )
    equations = (
        Equations[str]
        .context_model_validate(
            obj=loads(
                equations_path.read_text("utf-8") if equations_path.exists() else ""
            ),
            context=get_raw_equations_context(symbols=SYMS),
        )
        .model_dump()
    )
    for group in ["Group 1", "Group 3", "Group 4", "Group 5"]:
        content += f"\n## {group}\n"
        for name, eq in equations.items():
            if GROUPS[name] == group:
                eq = prep_equation_forms(equations[name])["latex"]  # pyright: ignore[reportArgumentType]
                content += dedent(f"""
                    ### {name}

                    $$
                    {eq}
                    $$ (eq_{"corr"}_{name})
                    """)
    (OUT / f"{corr}.md").write_text(encoding="utf-8", data=content.lstrip())


if __name__ == "__main__":
    main()
