"""Find bubbles as blobs."""

from cv2 import COLOR_GRAY2RGB

from boilercv.colors import RED
from boilercv.images.cv import apply_mask, build_mask_from_polygons, convert_image
from boilercv.types import ArrInt
from boilercv_pipeline.captivate.previews import edit_roi, view_images
from boilercv_pipeline.examples import EXAMPLE_FRAME_LIST, EXAMPLE_ROI
from boilercv_pipeline.examples.blobs import draw_blobs, get_blobs_doh

_NUM_FRAMES = 10
SHORTER_FRAME_LIST = EXAMPLE_FRAME_LIST[:_NUM_FRAMES]


def main():  # noqa: D103
    roi = edit_roi(SHORTER_FRAME_LIST[0], EXAMPLE_ROI)
    # results_log: list[ArrInt] = []
    # results_dog: list[ArrInt] = []
    results_doh: list[ArrInt] = []
    all_results = [
        # results_log,
        # results_dog,
        results_doh
    ]
    for input_image in SHORTER_FRAME_LIST:
        image = apply_mask(input_image, build_mask_from_polygons(input_image, [roi]))
        all_blobs = [
            # get_blobs_log(image),
            # get_blobs_dog(image),
            get_blobs_doh(image)
        ]
        sequence = zip(all_blobs, all_results, strict=True)
        for blobs, results in sequence:
            result = convert_image(input_image, COLOR_GRAY2RGB)
            for blob in blobs:
                draw_blobs(result, blob, RED)
            results.append(result)
    view_images([SHORTER_FRAME_LIST, *all_results])


if __name__ == "__main__":
    main()
