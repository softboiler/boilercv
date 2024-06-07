"""Make the equation documentation."""

from pathlib import Path
from textwrap import dedent
from tomllib import loads

from boilercv.correlations.models import Equations, prep_equation_forms
from boilercv.correlations.types import Corr
from boilercv_pipeline.equations import EQUATIONS, SYMS, get_raw_equations_context

PATH = Path("docs") / "experiments" / "e230920_subcool" / "_correlations.md"


def main():  # noqa: D103
    corr: Corr = "beta"
    equations_path = EQUATIONS[corr]
    content: str = ""
    equations = Equations[str].context_model_validate(
        obj=loads(equations_path.read_text("utf-8") if equations_path.exists() else ""),
        context=get_raw_equations_context(symbols=SYMS[corr]),
    )
    for name, eq in equations.items():
        eq = prep_equation_forms(eq.model_dump())["latex"]  # pyright: ignore[reportArgumentType]
        content += dedent(f"""
            ## {name}

            $$
            {eq}
            $$ (eq_{name})
            """)
    PATH.write_text(encoding="utf-8", data=content.lstrip())


if __name__ == "__main__":
    main()
