"""Parse equations.

Since we only run this locally to process paper equations using PyTorch and CUDA, don't
bog down CI with the slow installation from the extra index URL. Use `pipx` to isolate
this script's dependencies from the rest of the project:

    ```Shell
    pipx run scripts/convert_png_to_latex.py --pip-args '--extra-index-url=https://download.pytorch.org/whl/cu121'
    ```
"""

# /// script
# requires-python = "==3.11"
# dependencies = [
#     "cyclopts==2.5.0",
#     "pillow==10.3.0",
#     "pix2tex==0.1.2",
#     "torch==2.2.2",
#     "torchaudio==2.2.2",
#     "torchvision==0.17.2",
# ]
# ///

from pathlib import Path

from cyclopts import App
from PIL import Image
from pix2tex.cli import LatexOCR  # pyright: ignore[reportMissingImports]

APP = App(help_format="markdown")
"""CLI."""


def main():
    """Invoke the CLI."""
    APP()


@APP.default
def convert_png_to_latex(img: Path):
    print(LatexOCR()(Image.open(img)))  # noqa: T201


if __name__ == "__main__":
    main()
