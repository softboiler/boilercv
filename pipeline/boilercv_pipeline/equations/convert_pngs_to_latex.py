"""Convert PNGs to LaTeX."""

from pathlib import Path
from shlex import quote, split
from subprocess import run

from loguru import logger
from tqdm import tqdm

from boilercv_pipeline.correlations import PIPX, PNGS
from boilercv_pipeline.correlations.dimensionless_bubble_diameter import (
    EQUATIONS,
    LATEX_REPLS,
)

PNG_PARSER = quote((Path("scripts") / "convert_png_to_latex.py").as_posix())
"""Escaped path to converter script suitable for `subprocess.run` invocation."""
INDEX = "https://download.pytorch.org/whl/cu121"
"""Extra index URL for PyTorch and CUDA dependencies."""


def main():  # noqa: D103
    for expression in tqdm(EQUATIONS):  # pyright: ignore[reportArgumentType, reportCallIssue]  1.1.356, tomlkit 0.12.4
        name = expression.name
        if not name:
            continue
        name = name.strip().replace("\n", "").replace("    ", "")
        png = PNGS / f"{name}.png"
        if not png.exists() or expression.forms.latex:
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
        for old, new in LATEX_REPLS.items():
            latex = latex.replace(old, new)
    #     toml[EQS][i][LATEX] = latex  # pyright: ignore[reportArgumentType, reportIndexIssue]  1.1.356, tomlkit 0.12.4
    # data = dumps(toml)
    # for old, new in TOML_REPL.items():
    #     data = data.replace(old, new)
    # TOML.write_text(encoding="utf-8", data=data)


if __name__ == "__main__":
    logger.info("Start making equations from clipboard.")
    main()
    logger.info("Finish making equations from clipboard.")
