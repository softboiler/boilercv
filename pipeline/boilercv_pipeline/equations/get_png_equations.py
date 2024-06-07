"""Create PNGs for new equations."""

from typing import get_args

from copykitten import paste_image
from cyclopts import App
from loguru import logger
from PIL import Image
from tqdm import tqdm

from boilercv.correlations.types import Corr, Equation
from boilercv_pipeline.equations import PNGS

APP = App()
"""CLI."""


def main():  # noqa: D103
    APP()


@APP.default
def default(corr: Corr = "beta", overwrite: bool = False):  # noqa: D103, ARG001
    pngs = PNGS[corr]
    logger.info("Start making equations from clipboard.")
    for name in tqdm(get_args(Equation)):
        png = pngs / f"{name}.png"
        if not name or png.exists():
            continue
        input(f"\n\nPlease snip '{corr}' equation '{name}' to the clipboard...")
        pixels, width, height = paste_image()
        img = Image.frombytes(mode="RGBA", size=(width, height), data=pixels)
        img.convert("RGB").save(png)
    logger.info("Finish making equations from clipboard.")


if __name__ == "__main__":
    main()
