"""Detect the boiling surface."""

from warnings import warn

from cv2 import CHAIN_APPROX_SIMPLE, blur, cornerHarris
from numpy import array, count_nonzero, round
from scipy.ndimage import (
    center_of_mass,
    generate_binary_structure,
    label,
    labeled_comprehension,
)
from xarray import apply_ufunc

from boilercv.data import ROI, VIDEO, YX_PX, apply_to_img_da
from boilercv.data.frames import df_points
from boilercv.images import scale_bool
from boilercv.images.cv import find_contours, get_wall
from boilercv.types import DA, ArrInt, Img
from boilercv_pipeline import PREVIEW
from boilercv_pipeline.captivate.previews import (
    get_calling_scope_name,
    save_roi,
    view_images,
)
from boilercv_pipeline.examples import (
    EXAMPLE_NUM_FRAMES,
    EXAMPLE_ROI,
    EXAMPLE_VIDEO_NAME,
)
from boilercv_pipeline.sets import get_dataset


def main():
    """Detect the boiling surface."""
    ds = get_dataset(EXAMPLE_VIDEO_NAME, EXAMPLE_NUM_FRAMES)
    _video = ds[VIDEO]
    roi = ds[ROI]
    wall: DA = apply_to_img_da(get_wall, scale_bool(roi), name="wall")
    boiling_surface, _boiling_surface_coords = apply_ufunc(
        find_boiling_surface,
        scale_bool(wall),
        input_core_dims=[YX_PX],
        output_core_dims=[YX_PX, ["test"]],
    )
    contours = find_contours(scale_bool(wall.values), method=CHAIN_APPROX_SIMPLE)
    if len(contours) > 1:
        warn("More than one contour found when searching for the ROI.", stacklevel=1)
    save_roi(contours[0], EXAMPLE_ROI)
    view_images(dict(boiling_surface=boiling_surface, roi=roi))


def find_boiling_surface(img: Img) -> tuple[Img, ArrInt]:
    """Find the boiling surface."""
    # Parameters for finding prominent horizontal lines
    wide_rectangular_ksize = [9, 3]  # Enhance horizontal lines
    threshold = 0.6

    # The range to consider a connected component to be the boiling surface
    (height, width) = img.shape
    min_size_px = 8
    ypx_min = height / 2
    xpx_mid = width / 2
    xpx_max_dist = width / 8
    xpx_min = xpx_mid - xpx_max_dist
    xpx_max = xpx_mid + xpx_max_dist

    # Find prominent horizontal lines
    corners = cornerHarris(src=img, blockSize=2, ksize=3, k=0.04)
    lines = -1 * corners  # pyright: ignore[reportOperatorIssue]
    blurred = blur(lines, ksize=wide_rectangular_ksize)
    scaled = (blurred - blurred.min()) / (blurred.max() - blurred.min())
    binarized = scaled > threshold

    # Find connected components and their centers
    # ? cv2.connectedComponents and cv2.moments could also be used
    # ? Consider re-implementing if slow
    find_diag_conns = generate_binary_structure(rank=2, connectivity=2)
    labeled_img, num_objects = label(input=binarized, structure=find_diag_conns)  # pyright: ignore[reportGeneralTypeIssues]
    labels = range(1, num_objects + 1)  # Exclude 0-labeled background
    sizes_px = labeled_comprehension(
        input=binarized,
        labels=labeled_img,
        index=labels,
        func=count_nonzero,
        out_dtype=int,
        default=0,
    )
    objs = (
        df_points(
            array(center_of_mass(input=binarized, labels=labeled_img, index=labels))
            .round()
            .astype(int)  # Not img dtype. df contains coords, not pixel values
        )
        .assign(**dict(label=labels, size_px=sizes_px))
        .rename(axis="columns", mapper=dict(ypx="ypx_center", xpx="xpx_center"))
        .set_index("label", drop=True)
    )

    # Consider the boiling surface to be the largest object in range
    objs_in_range = objs[
        (objs.size > min_size_px)
        & (objs.ypx_center > ypx_min)
        & (objs.xpx_center > xpx_min)
        & (objs.xpx_center < xpx_max)
    ]
    label_largest_in_range = objs_in_range.size_px.idxmax()
    boiling_surface = labeled_img == label_largest_in_range

    # Get a line segment corresponding to the boiling surface
    points = df_points(array(boiling_surface.nonzero()).T)
    xpx_left = points.xpx.min()
    xpx_right = points.xpx.max()
    ypx_horizontal = round(points.ypx.mean()).astype(int)
    boiling_surface_coords = array([
        ypx_horizontal,
        xpx_left,
        ypx_horizontal,
        xpx_right,
    ]).astype(int)

    if PREVIEW:
        view_images(
            name=get_calling_scope_name(),
            images=dict(
                img=img,
                corners=corners,
                lines=lines,
                blurred=blurred,
                scaled=scaled,
                binarized=binarized,
                labeled_img=labeled_img,
                boiling_surface=boiling_surface,
            ),
        )
    return boiling_surface, boiling_surface_coords


if __name__ == "__main__":
    main()
