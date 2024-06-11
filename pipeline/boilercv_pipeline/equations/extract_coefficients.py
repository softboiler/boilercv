"""Extract coefficients for quick comparison to literature."""

from re import findall
from sys import stdout
from textwrap import dedent
from tomllib import loads

from cyclopts import App
from loguru import logger

from boilercv.correlations import GROUPS
from boilercv.correlations.models import Equations, prep_equation_forms
from boilercv.correlations.types import Corr
from boilercv_pipeline.equations import EQUATIONS, SYMS, get_raw_equations_context

logger.remove()
logger.add(sink=stdout, format="<level>{message}</level>")

APP = App()
"""CLI."""


def main():  # noqa: D103
    APP()


@APP.default
def default(corr: Corr = "beta"):  # noqa: D103
    logger.warning("")
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
                eq = [m.strip() for m in findall(r"[\d \-/.]+", eq) if m.strip()]
                content += dedent(f"""
                    ### {name}

                    {eq}
                    """)
    logger.info(content.lstrip())


if __name__ == "__main__":
    main()
