"""Basic examples using OpenCV sample files."""

from collections.abc import Iterator
from os import environ
from pathlib import Path

from cv2 import VideoCapture

from boilercv.types import Img


def init():
    """Initialize `boilercv.examples.cv`."""
    check_samples_env_var()


def check_samples_env_var():
    """Check that the OpenCV samples environment variable is set and is a folder."""
    samples_env_var = "OPENCV_SAMPLES_DATA_PATH"
    if (
        not (samples_dir := environ.get(samples_env_var))
        or not Path(samples_dir).is_dir()
    ):
        raise RuntimeError(
            f"{samples_env_var} not set or specified directory does not exist."
        )


def capture_images(path: Path) -> Iterator[Img]:
    """Load images from a video file."""
    video_capture = VideoCapture(str(path))
    while True:
        read_is_successful, image = video_capture.read()
        if not read_is_successful:
            break
        yield image  # pyright: ignore[reportReturnType]


# * -------------------------------------------------------------------------------- * #

init()
