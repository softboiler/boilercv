"""Process images with OpenCV."""

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

from cv2 import (
    ADAPTIVE_THRESH_MEAN_C,
    BORDER_CONSTANT,
    CHAIN_APPROX_NONE,
    FILLED,
    FLOODFILL_MASK_ONLY,
    MORPH_BLACKHAT,
    MORPH_CLOSE,
    MORPH_CROSS,
    MORPH_DILATE,
    MORPH_ELLIPSE,
    MORPH_ERODE,
    MORPH_GRADIENT,
    MORPH_HITMISS,
    MORPH_OPEN,
    MORPH_RECT,
    MORPH_TOPHAT,
    RETR_EXTERNAL,
    THRESH_BINARY,
    LineSegmentDetector,
    adaptiveThreshold,
    add,
    bitwise_not,
    copyMakeBorder,
    createLineSegmentDetector,
    cvtColor,
    drawContours,
    fillPoly,
    findContours,
    floodFill,
    getStructuringElement,
    morphologyEx,
)
from numpy import array, flip, fliplr, iinfo, zeros_like

from boilercv.colors import WHITE, WHITE3
from boilercv.images import unpad
from boilercv.types import ArrFloat, ArrInt, Img, ImgBool


def convert_image(img: Img, code: int | None = None) -> Img:
    """Convert image format, handling inconsistent type annotations."""
    return cvtColor(img, code)  # pyright: ignore[reportArgumentType, reportCallIssue]


def apply_mask(img: Img, mask: Img) -> Img:
    """Mask an image, keeping parts where the mask is bright."""
    return add(img, bitwise_not(mask))  # pyright: ignore[reportReturnType]


def pad(img: Img, pad_width: int, value: int) -> Img:
    """Pad an image with a constant value.

    Parameters
    ----------
    img
        Image.
    pad_width
        Width of the pad, in pixels.
    value
        Pixel value to fill the pad with.

    Returns
    -------
    img:
        Padded image.
    """
    return copyMakeBorder(
        img,
        top=pad_width,
        bottom=pad_width,
        left=pad_width,
        right=pad_width,
        borderType=BORDER_CONSTANT,
        value=value,  # pyright: ignore[reportArgumentType, reportCallIssue]
    )


def binarize(img: Img, block_size: int = 11, thresh_dist_from_mean: int = 2) -> ImgBool:
    """Binarize an image with an adaptive threshold."""
    block_size += 1 if block_size % 2 == 0 else 0
    return adaptiveThreshold(
        src=img,
        maxValue=iinfo(img.dtype).max,
        adaptiveMethod=ADAPTIVE_THRESH_MEAN_C,
        thresholdType=THRESH_BINARY,
        blockSize=block_size,
        C=thresh_dist_from_mean,
    ).astype(bool)


def flood(img: Img) -> ImgBool:
    """Flood the image, returning the resulting flood as a bright mask."""
    seed_point = array(img.shape) // 2
    _max_value = iinfo(img.dtype).max
    # OpenCV needs a masked array with a one-pixel pad
    pad_width = 1
    mask = pad(zeros_like(img), pad_width, value=1)
    _retval, _image, mask, _rect = floodFill(
        image=img,
        mask=mask,
        seedPoint=tuple(flip(seed_point)),  # OpenCV expects (x, y)
        newVal=None,  # pyright: ignore[reportArgumentType, reportCallIssue]
        flags=FLOODFILL_MASK_ONLY,
    )
    # Return the mask in original dimensions
    return unpad(mask, pad_width).astype(bool)


def close_and_erode(img: Img) -> Img:
    """Close holes, then erode."""
    return transform(img, [Transform(Op.close, 4), Transform(Op.erode, 9)]).astype(bool)


def get_wall(roi: Img) -> Img:
    """Dilate the ROI to get the wall."""
    return transform(roi, Transform(Op.dilate, 9)).astype(bool)


class Op(Enum):
    """A morphological transform operation."""

    black_hat = MORPH_BLACKHAT
    close = MORPH_CLOSE
    cross = MORPH_CROSS
    dilate = MORPH_DILATE
    ellipse = MORPH_ELLIPSE
    erode = MORPH_ERODE
    gradient = MORPH_GRADIENT
    hitmiss = MORPH_HITMISS
    open = MORPH_OPEN
    rect = MORPH_RECT
    top_hat = MORPH_TOPHAT


@dataclass
class Transform:
    """A morphological transform."""

    op: Op
    """The transform to perform."""
    size: int
    """The elliptical kernel size."""


def transform(img: Img, transforms: Transform | Sequence[Transform]) -> Img:
    """Apply morphological transforms to an image with a dark background."""
    transforms = [transforms] if isinstance(transforms, Transform) else transforms
    pad_width = max(transform.size for transform in transforms)
    # Explicitly pad out the image since cv2.morphologyEx boundary handling is weird
    img = pad(img, pad_width, value=0)
    for transform in transforms:
        img = morphologyEx(  # pyright: ignore[reportAssignmentType]
            src=img,
            op=transform.op.value,
            kernel=getStructuringElement(MORPH_ELLIPSE, [transform.size] * 2),
        )
    return unpad(img, pad_width)


def build_mask_from_polygons(img: Img, contours: Sequence[ArrInt]) -> Img:
    """Build a mask from the intersection of a sequence of polygonal contours."""
    # OpenCV expects contours as shape (N, 1, 2) instead of (N, 2)
    contours = [fliplr(contour).reshape(-1, 1, 2) for contour in contours]
    blank = zeros_like(img)
    return fillPoly(  # pyright: ignore[reportReturnType]
        img=blank,
        pts=contours,  # Expects a list of coordinates, we have just one
        color=WHITE3,
    )


def find_contours(img: Img, method: int = CHAIN_APPROX_NONE) -> list[ArrInt]:
    """Find external contours of bright objects in an image."""
    contours, _hierarchy = findContours(
        image=img,
        mode=RETR_EXTERNAL,  # No hierarchy needed because we keep external contours
        method=method,
    )
    # Images have dims (y, x) and shape (h, w). We want the dims of returned contours to
    # match that. OpenCV returns a list of contours. Each contour has dims (point, 1,
    # pair), where "point" are the points making up a contour and "pair" are the (x, y)
    # coordinates of each point. Reshape each contour to dims (point, pair), then flip
    # the order of pairs to (x, y).
    return [fliplr(contour.reshape(-1, 2)) for contour in contours]  # pyright: ignore[reportReturnType]


def draw_contours(
    img: Img,
    contours: Sequence[ArrInt],
    contour_index: int = -1,
    thickness: int = FILLED,
    color: int | tuple[int, ...] = WHITE,
) -> Img:
    """Draw contours on an image."""
    # Each contour has dims (point, pair), where "point" are the points making up a
    # contour and "pair" are the (x, y) coordinates of each point. OpenCV expects each
    # contour to have dims (point, 1, pair), with "pair" order (x, y). Flip the order of
    # each contour's pairs to (y, x), then reshape each contour to dims (point, 1,
    # pair).
    return drawContours(
        image=img.copy(),
        contours=[fliplr(contour).reshape(-1, 1, 2) for contour in contours],
        contourIdx=contour_index,
        color=color,  # pyright: ignore[reportArgumentType, reportCallIssue]
        thickness=thickness,
    )


def find_line_segments(img: Img) -> tuple[ArrFloat, LineSegmentDetector]:
    """Find line segments in an image."""
    lsd = createLineSegmentDetector()
    lines, *_ = lsd.detect(img)
    # OpenCV returns line segments as shape (N, 1, 4) instead of (N, 4)
    lines = lines.reshape(-1, 4)
    return lines, lsd  # pyright: ignore[reportReturnType]
