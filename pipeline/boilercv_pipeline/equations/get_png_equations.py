"""Create PNGs for new equations in `equations.toml`."""

from copykitten import paste_image
from loguru import logger
from PIL import Image
from tqdm import tqdm

from boilercv_pipeline.correlations import PNGS
from boilercv_pipeline.correlations.dimensionless_bubble_diameter import EQUATIONS


def main():  # noqa: D103
    for expression in tqdm(EQUATIONS):  # pyright: ignore[reportArgumentType, reportCallIssue]  1.1.356, tomlkit 0.12.4
        name = expression.name
        png = PNGS / f"{name}.png"
        if not name or png.exists():
            continue
        input(f"\n\nPlease snip equation `{name}` to your clipboard...")
        pixels, width, height = paste_image()
        img = Image.frombytes(mode="RGBA", size=(width, height), data=pixels)
        img.convert("RGB").save(png)
    # TOML.write_text(encoding="utf-8", data=dumps(toml))


if __name__ == "__main__":
    logger.info("Start making equations from clipboard.")
    main()
    logger.info("Finish making equations from clipboard.")
