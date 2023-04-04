"""Given an MP4, find ROI using `opencv` and find contours."""

import cv2 as cv
import numpy as np
from scipy.spatial import ConvexHull

from boilercv.colors import BLUE_CV
from boilercv.examples import capture_images
from boilercv.images import scale_bool
from boilercv.images.cv import (
    binarize,
    build_mask_from_polygons,
    convert_image,
    draw_contours,
    find_contours,
)
from boilercv.models.params import PARAMS
from boilercv.types import ArrInt

WINDOW_NAME = "image"
ESC_KEY = ord("\x1b")


def main():
    images = (
        image[:, :, 0]
        for image in capture_images(
            PARAMS.paths.examples / "2022-04-08T16-12-42_short.mp4"
        )
    )
    roi = get_roi(next(images))
    for image in images:
        masked = build_mask_from_polygons(image, [roi])
        thresholded = binarize(masked)
        contours = find_contours(scale_bool(thresholded))
        image_with_contours = draw_contours(image, contours)
        cv.imshow(WINDOW_NAME, image_with_contours)
        if cv.waitKey(100) == ESC_KEY:
            break
    cv.destroyAllWindows()


def get_roi(image: ArrInt) -> ArrInt:
    """Get the region of interest of an image.

    See: https://docs.opencv.org/4.6.0/db/d5b/tutorial_py_mouse_handling.html
    """

    clicks: list[tuple[int, int]] = []

    image = convert_image(image, cv.COLOR_GRAY2RGB)
    (width, height) = image.shape[:-1]
    click = 0
    default_clicks = [(0, 0), (0, width), (height, width), (height, 0)]
    hull = ConvexHull(default_clicks)
    hull_minimum_vertices = 3
    composite_image = image

    def main() -> ArrInt:
        nonlocal clicks
        cv.imshow(WINDOW_NAME, image)
        cv.setMouseCallback(WINDOW_NAME, handle_mouse_events)
        while True and cv.waitKey(100) != ESC_KEY:
            pass
        if len(clicks) < hull_minimum_vertices:
            clicks = default_clicks
        else:
            hull.close()
        return np.array(clicks)[hull.vertices]

    def handle_mouse_events(event: int, x: int, y: int, *_):
        """Handle all mouse events. Form a convex hull from left clicks."""
        nonlocal image, click, hull, composite_image
        if event == cv.EVENT_LBUTTONDOWN:
            click += 1
            clicks.append((x, y))
            image = cv.drawMarker(image, clicks[-1], BLUE_CV)
            if click == hull_minimum_vertices:
                hull = ConvexHull(clicks, incremental=True)
                composite_image = draw_hull(hull, image)
            elif click > hull_minimum_vertices:
                hull.add_points([clicks[-1]])
                composite_image = draw_hull(hull, image)
            cv.imshow(WINDOW_NAME, composite_image)

    def draw_hull(hull: ConvexHull, image: ArrInt) -> ArrInt:
        """Draw a convex hull on the image."""
        image = image.copy()
        clicks = hull.points.astype(int)
        for simplex in hull.simplices:
            image = cv.line(image, clicks[simplex[0]], clicks[simplex[1]], BLUE_CV)
        return image

    return main()


if __name__ == "__main__":
    main()
