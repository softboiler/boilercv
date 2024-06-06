"""Convert PNGs to LaTeX."""

from pathlib import Path
from shlex import quote, split
from subprocess import run
from tomllib import loads

from cyclopts import App
from loguru import logger
from tomlkit import TOMLDocument, parse
from tqdm import tqdm

from boilercv.mappings import sync
from boilercv_pipeline.correlations import PIPX, PNGS
from boilercv_pipeline.correlations.dimensionless_bubble_diameter import (
    EQUATIONS_TOML,
    LATEX_REPLS,
)
from boilercv_pipeline.correlations.models import Equations
from boilercv_pipeline.equations import default_syms

PNG_PARSER = quote((Path("scripts") / "convert_png_to_latex.py").as_posix())
"""Escaped path to converter script suitable for `subprocess.run` invocation."""
INDEX = "https://download.pytorch.org/whl/cu121"
"""Extra index URL for PyTorch and CUDA dependencies."""
APP = App()
"""CLI."""


def main():  # noqa: D103
    APP()


@APP.default
def default(  # noqa: D103
    equations: Path = EQUATIONS_TOML,
    symbols: tuple[str, ...] = default_syms,
    overwrite: bool = False,
):
    logger.info("Start converting images of equations to LaTeX.")
    equations_content = equations.read_text("utf-8") if equations.exists() else ""
    eqns = Equations.context_model_validate(
        obj=loads(equations_content), context=Equations.get_context(symbols=symbols)
    )
    for name, eq in tqdm(eqns.items()):
        png = PNGS / f"{name}.png"
        if (not overwrite and not png.exists()) or eq.latex:
            continue
        sep = " "
        result = run(
            args=split(
                sep.join([
                    f"{PIPX} run --pip-args '--extra-index-url {INDEX}' --",
                    f"{PNG_PARSER} {quote(png.as_posix())}",
                ])
            ),
            capture_output=True,
            check=False,
            text=True,
        )
        if result.returncode:
            raise RuntimeError(result.stderr)
        latex = result.stdout.strip()
        for repl in LATEX_REPLS:
            latex = latex.replace(repl.find, repl.repl)
    equations.write_text(
        encoding="utf-8",
        data=(
            sync(
                reference=eqns.model_dump(mode="json"),
                target=TOMLDocument() if overwrite else parse(equations_content),
            )
        ).as_string(),
    )
    #     toml[EQS][i][LATEX] = latex  # pyright: ignore[reportArgumentType, reportIndexIssue]  1.1.356, tomlkit 0.12.4
    # data = dumps(toml)
    # for old, new in TOML_REPL.items():
    #     data = data.replace(old, new)
    # TOML.write_text(encoding="utf-8", data=data)
    logger.info("Finish generating symbolic equations.")


if __name__ == "__main__":
    main()
