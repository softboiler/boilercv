"""Create PNGs for new equations."""

from typing import get_args

from copykitten import paste_image
from loguru import logger
from PIL import Image
from tqdm import tqdm

from boilercv_pipeline.correlations import PNGS
from boilercv_pipeline.correlations.types import Equation


def main():  # noqa: D103
    for name in tqdm(get_args(Equation)):
        png = PNGS / f"{name}.png"
        if not name or png.exists():
            continue
        input(f"\n\nPlease snip equation `{name}` to the clipboard...")
        pixels, width, height = paste_image()
        img = Image.frombytes(mode="RGBA", size=(width, height), data=pixels)
        img.convert("RGB").save(png)


if __name__ == "__main__":
    logger.info("Start making equations from clipboard.")
    main()
    logger.info("Finish making equations from clipboard.")
