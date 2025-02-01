"""Preview a video."""

from pathlib import Path

from cv2 import COLOR_BGR2RGB
from cv2.samples import findFile
from numpy import stack

from boilercv.images.cv import convert_image
from boilercv.types import Vid
from boilercv_pipeline import PREVIEW
from boilercv_pipeline.captivate.previews import view_images
from boilercv_pipeline.examples.cv import capture_images


def main(preview: bool = PREVIEW) -> Vid:
    images = capture_images(Path(findFile("vtest.avi")))
    video = stack([convert_image(image, COLOR_BGR2RGB) for image in images])
    if preview:
        view_images(video)
    return video


if __name__ == "__main__":
    main()
