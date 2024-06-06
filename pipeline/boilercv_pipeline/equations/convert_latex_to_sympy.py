"""Convert LaTeX equations to SymPy equations."""

from pathlib import Path
from re import finditer
from shlex import quote, split
from subprocess import run
from tomllib import loads

from cyclopts import App
from loguru import logger
from tomlkit import parse
from tqdm import tqdm

from boilercv.mappings import Repl, replace_pattern, sync
from boilercv_pipeline.correlations import PIPX
from boilercv_pipeline.correlations.models import EquationForms, Equations, Forms
from boilercv_pipeline.equations import default_equations, default_syms

LATEX_PARSER = Path("scripts") / "convert_latex_to_sympy.py"
"""Isolated LaTeX parser."""
APP = App()
"""CLI."""


def main():  # noqa: D103
    APP()


@APP.default
def default(  # noqa: D103
    equations: Path = default_equations, symbols: tuple[str, ...] = default_syms
):
    logger.info("Start converting LaTeX expressions to SymPy expressions.")

    # ? Don't process strings
    forms_context = Forms.get_context(symbols=symbols)
    forms_context.pipelines[Forms].before = (forms_context.pipelines[Forms].before[0],)
    context = Equations[str].get_context(symbols=symbols, forms_context=forms_context)

    # ? Parse equations
    equations_content = equations.read_text("utf-8") if equations.exists() else ""
    parsed_eqns = (
        Equations[str]
        .context_model_validate(obj=loads(equations_content), context=context)
        .morph_cpipe(parse_equations, context)
    )

    # ? Update the TOML file with changes
    toml = sync(
        reference=parsed_eqns.model_dump(mode="json"), target=parse(equations_content)
    )

    # ? Convert escaped strings to raw strings
    content = toml.as_string()
    for match in finditer(r'"[^"]*"', content):
        old_eq = new_eq = match.group()
        for old, new in {'"': "'", r"\\": "\\"}.items():
            new_eq = new_eq.replace(old, new)
        content = content.replace(old_eq, new_eq)

    # ? Write the result
    equations.write_text(encoding="utf-8", data=content)

    logger.info("Finish converting LaTeX expressions to SymPy expressions.")


def parse_equations(equations: Equations[str]) -> Equations[str]:
    """Parse equations."""
    for name, eq in tqdm(equations.items()):
        if not eq.latex:
            continue
        if eq.sympy:
            continue
        equations[name] = convert(forms=eq, interpreter=PIPX, script=LATEX_PARSER)
    return equations


def convert(
    forms: EquationForms[str], interpreter: Path, script: Path
) -> EquationForms[str]:
    """Convert LaTeX equation to SymPy equation."""
    sanitized_latex = replace_pattern(
        forms.model_dump(),
        (
            Repl(src="latex", dst="latex", find=find, repl=repl)
            for find, repl in {r"\\left\(": "(", r"\\right\)": ")"}.items()
        ),
    )["latex"]
    result = run(
        args=split(
            f"{escape(interpreter)} run {escape(script)} {quote(sanitized_latex)}"
        ),
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr)
    forms.sympy = result.stdout.strip()
    return forms


def escape(path: Path) -> str:
    """Escape path for running subprocesses."""
    return quote(path.as_posix())


if __name__ == "__main__":
    main()
