"""Convert LaTeX equations to SymPy equations."""

from pathlib import Path
from shlex import quote, split
from subprocess import run
from tomllib import loads
from typing import get_args

from cyclopts import App
from loguru import logger
from tomlkit import parse
from tqdm import tqdm

from boilercv.correlations.models import EquationForms, Equations
from boilercv.correlations.pipes import fold_whitespace
from boilercv.correlations.types import Corr, Kind
from boilercv.mappings import Repl, replace, replace_pattern, sync
from boilercv.morphs.contexts import Defaults
from boilercv.morphs.morphs import Morph
from boilercv_pipeline.equations import (
    EQUATIONS,
    PIPX,
    SYMS,
    escape,
    get_raw_equations_context,
    make_raw,
    sanitize_forms,
)

LATEX_PARSER = Path("scripts") / "convert_latex_to_sympy.py"
"""Isolated LaTeX parser."""
APP = App()
"""CLI."""


def main():  # noqa: D103
    APP()


@APP.default
def default(corr: Corr = "beta", overwrite: bool = False):  # noqa: D103
    equations_path = EQUATIONS[corr]
    logger.info("Start converting LaTeX expressions to SymPy expressions.")
    content = equations_path.read_text("utf-8") if equations_path.exists() else ""
    symbols = SYMS[corr]
    context = get_raw_equations_context(symbols=symbols)
    equations = (
        Equations[str]
        .context_model_validate(obj=loads(content), context=context)
        .morph_cpipe(parse_equations, context, symbols=symbols, overwrite=overwrite)
    )
    equations_path.write_text(
        encoding="utf-8",
        data=make_raw(
            sync(
                reference=equations.model_dump(mode="json"), target=parse(content)
            ).as_string()
        ),
    )
    logger.info("Finish converting LaTeX expressions to SymPy expressions.")


def parse_equations(
    equations: Equations[str], symbols: tuple[str, ...], overwrite: bool
) -> Equations[str]:
    """Parse equations."""
    for name, eq in tqdm(equations.items()):
        if not overwrite and (eq.sympy or not eq.latex):
            continue
        equations[name] = convert(
            forms=eq, symbols=symbols, interpreter=PIPX, script=LATEX_PARSER
        )
    return equations


def convert(
    forms: EquationForms[str], symbols: tuple[str, ...], interpreter: Path, script: Path
) -> EquationForms[str]:
    """Convert LaTeX equation to SymPy equation."""
    sanitized_latex = replace_pattern(
        sanitize_forms(forms, symbols, sanitizer=sanitize_and_fold).model_dump(),
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
    return sanitize_forms(forms, symbols, sanitizer=sanitize)


def sanitize_and_fold(
    forms: dict[Kind, str], symbols: tuple[str, ...]
) -> Morph[Kind, str]:
    """Sanitize and fold symbolic forms."""
    return (
        Morph[Kind, str](forms)
        .morph_pipe(sanitize, symbols=symbols)
        .morph_pipe(fold_whitespace, Defaults(keys=get_args(Kind)))
    )


def sanitize(forms: dict[Kind, str], symbols: tuple[str, ...]) -> Morph[Kind, str]:
    """Sanitize symbolic forms."""
    return (
        Morph[Kind, str](forms)
        .morph_pipe(
            replace,
            (
                Repl[Kind](src="sympy", dst="sympy", find=find, repl=repl)
                for find, repl in {"{o}": "0", "{bo}": "b0"}.items()
            ),
        )
        .morph_pipe(
            replace_pattern,
            (
                Repl[Kind](src="sympy", dst="sympy", find=find, repl=repl)
                for sym in symbols
                for find, repl in {
                    # ? Symbol split by `(` after first character.
                    rf"{sym[0]}\*\({sym[1:]}([^)]+)\)": rf"{sym}\g<1>",
                    # ? Symbol split by a `*` after first character.
                    rf"{sym[0]}\*{sym[1:]}": rf"{sym}",
                    # ? Symbol missing `*` resulting in failed attempt to call it
                    rf"{sym}\(": rf"{sym}*(",
                }.items()
            ),
        )
    )


if __name__ == "__main__":
    main()
