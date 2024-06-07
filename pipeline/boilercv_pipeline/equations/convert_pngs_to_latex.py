"""Convert PNGs to LaTeX."""

from pathlib import Path
from re import finditer
from shlex import split
from subprocess import run
from tomllib import loads

from cyclopts import App
from loguru import logger
from tomlkit import parse
from tqdm import tqdm

from boilercv.correlations.models import Equations
from boilercv.correlations.types import Corr
from boilercv.mappings import sync
from boilercv_pipeline.equations import EQUATIONS, PIPX, PNGS, SYMS, escape

PNG_PARSER = Path("scripts") / "convert_png_to_latex.py"
"""Path to converter script suitable for `subprocess.run` invocation."""
INDEX = "https://download.pytorch.org/whl/cu121"
"""Extra index URL for PyTorch and CUDA dependencies."""
APP = App()
"""CLI."""

# symbols_without_script = [s.split("_")[0] for s in symbols]
# forms = replace(
#     forms,
#     (
#         Repl[Kind](src="latex", dst="latex", find=find, repl=repl)
#         for find, repl in {
#             **{" ".join(s): s for s in symbols_without_script},
#             **{s: rf" \{s}" for s in symbols_without_script if len(s) < 3},
#             **{rf"\{s}": rf" \{s}" for s in symbols_without_script if len(s) >= 3},
#             "F O": "Fo",
#             "F 0": "Fo",
#             "J a": "Ja",
#             "{bo}": r"\bo",
#             "{b0}": r"\bo",
#             "{00}": r"\bo",
#             "{o}": r"\o",
#             "{0}": r"\o",
#             "}": "} ",
#             "(": " (",
#         }.items()
#     ),
# )


def main():  # noqa: D103
    APP()


@APP.default
def default(corr: Corr = "beta", overwrite: bool = False):  # noqa: D103
    symbols = SYMS[corr]
    equations = EQUATIONS[corr]
    pngs = PNGS[corr]

    logger.info("Start converting images of equations to LaTeX.")

    equations_content = equations.read_text("utf-8") if equations.exists() else ""
    context = Equations[str].get_context(symbols=symbols)
    eqns = Equations[str].context_model_validate(
        obj=loads(equations_content), context=context
    )
    for name, eq in tqdm(eqns.items()):
        png = pngs / f"{name}.png"
        if (not overwrite and not png.exists()) or eq.latex:
            continue
        sep = " "
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
        eqns[name].latex = result.stdout.strip()

    # ? Update the TOML file with changes
    toml = sync(
        reference=eqns.context_model_validate(
            eqns.model_dump(), context=context
        ).model_dump(mode="json"),
        target=parse(equations_content),
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

    logger.info("Finish generating symbolic equations.")


if __name__ == "__main__":
    main()
