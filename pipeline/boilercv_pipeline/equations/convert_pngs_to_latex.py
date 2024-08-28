"""Convert PNGs to LaTeX."""

from pathlib import Path
from shlex import split
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
from boilercv.mappings import Repl, replace, sync
from boilercv.morphs.morphs import Morph
from boilercv.morphs.pipelines import Defaults
from boilercv_pipeline.equations import (
    EQUATIONS,
    PIPX,
    PNGS,
    SYMS,
    escape,
    get_raw_equations_context,
    make_raw,
    sanitize_forms,
)

PNG_PARSER = Path("scripts") / "convert_png_to_latex.py"
"""Path to converter script suitable for `subprocess.run` invocation."""
INDEX = "https://download.pytorch.org/whl/cu121"
"""Extra index URL for PyTorch and CUDA dependencies."""
APP = App()
"""CLI."""


def main():  # noqa: D103
    APP()


@APP.default
def default(corr: Corr = "beta", overwrite: bool = False):  # noqa: D103
    equations_path = EQUATIONS[corr]
    logger.info("Start converting images of equations to LaTeX.")
    content = equations_path.read_text("utf-8") if equations_path.exists() else ""
    equations = (
        Equations[str]
        .model_validate(
            obj=loads(content), context=get_raw_equations_context(symbols=SYMS)
        )
        .morph_pipe(parse_equations, pngs=PNGS[corr], overwrite=overwrite, symbols=SYMS)
    )
    equations_path.write_text(
        encoding="utf-8",
        data=make_raw(
            sync(
                reference=equations.model_dump(mode="json"), target=parse(content)
            ).as_string()
        ),
    )
    logger.info("Finish converting images of equations to LaTeX.")


def parse_equations(
    equations: Equations[str], symbols: tuple[str, ...], pngs: Path, overwrite: bool
) -> Equations[str]:
    """Parse equations."""
    for name, eq in tqdm(equations.items()):
        png = pngs / f"{name}.png"
        if not overwrite and (eq.latex or not png.exists()):
            continue
        equations[name] = convert(forms=equations[name], png=png, symbols=symbols)
    return equations


def convert(
    forms: EquationForms[str], png: Path, symbols: tuple[str, ...]
) -> EquationForms[str]:
    """Convert PNGs to LaTeX."""
    sep = " "
    sanitize_forms(forms, symbols, sanitizer=sanitize)
    result = run(
        args=split(
            sep.join([
                f"{escape(PIPX)} run --pip-args '--extra-index-url {INDEX}' --",
                f"{escape(PNG_PARSER)} {escape(png)}",
            ])
        ),
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr)
    forms.latex = result.stdout.strip()
    return sanitize_forms(forms, symbols, sanitizer=sanitize)


def sanitize(forms: dict[Kind, str], symbols: tuple[str, ...]) -> Morph[Kind, str]:
    """Sanitize LaTeX forms."""
    syms_no_script = [s.split("_")[0] for s in symbols]
    return (
        Morph[Kind, str](forms)
        .morph_pipe(
            replace,
            (
                Repl[Kind](src="latex", dst="latex", find=find, repl=repl)
                for find, repl in {
                    **{" ".join(s): s for s in syms_no_script},
                    **{s: rf" \{s}" for s in syms_no_script if len(s) < 3},
                    **{rf"\{s}": rf" \{s}" for s in syms_no_script if len(s) >= 3},
                    "F O": "Fo",
                    "F 0": "Fo",
                    "J a": "Ja",
                    "{bo}": r"\bo",
                    "{b0}": r"\bo",
                    "{00}": r"\bo",
                    "{o}": r"\o",
                    "{0}": r"\o",
                    "}": "} ",
                    "(": " (",
                }.items()
            ),
        )
        .morph_pipe(fold_whitespace, Defaults(keys=get_args(Kind)))
    )


if __name__ == "__main__":
    main()
