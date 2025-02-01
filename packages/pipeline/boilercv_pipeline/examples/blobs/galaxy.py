"""Find blobs in the galaxy."""

from skimage import data
from skimage.color import rgb2gray

from boilercv.colors import BLUE, GREEN, RED
from boilercv.types import ArrInt
from boilercv_pipeline.captivate.previews import view_images
from boilercv_pipeline.examples.blobs import (
    draw_blobs,
    get_blobs_dog,
    get_blobs_doh,
    get_blobs_log,
)


def main():
    image = data.hubble_deep_field()[0:500, 0:500]  # pyright: ignore[reportAttributeAccessIssue]
    image_gray = rgb2gray(image)
    operations = {
        "Laplacian of Gaussian": get_blobs_log,
        "Difference of Gaussian": get_blobs_dog,
        "Determinant of Hessian": get_blobs_doh,
    }
    blobs = {title: func(image_gray) for title, func in operations.items()}
    results: dict[str, ArrInt] = {}
    for (title, blobs_), color in zip(blobs.items(), [RED, GREEN, BLUE], strict=True):
        results[title] = image.copy()
        for blob in blobs_:
            draw_blobs(results[title], blob, color)
    view_images({"input": image} | results)


if __name__ == "__main__":
    main()
