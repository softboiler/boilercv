"""Show an OpenCV sample image."""

from cv2 import COLOR_BGR2RGB, cvtColor, imread
from cv2.samples import findFile

from boilercv.types import ImgLike
from boilercv_pipeline import PREVIEW
from boilercv_pipeline.captivate.previews import view_images


def main(preview=PREVIEW) -> ImgLike:
    img = cvtColor(imread(findFile("starry_night.jpg")), COLOR_BGR2RGB)
    if preview:
        view_images(img)
    return img


if __name__ == "__main__":
    main()
