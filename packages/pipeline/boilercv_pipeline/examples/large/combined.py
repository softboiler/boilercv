"""Perform all of the steps."""

from boilercv.data import FRAME, VIDEO, apply_to_img_da
from boilercv.data.packing import pack
from boilercv.images import scale_bool
from boilercv.images.cv import apply_mask, binarize, close_and_erode, flood
from boilercv.types import DA
from boilercv_pipeline import DEBUG
from boilercv_pipeline.captivate.previews import view_images
from boilercv_pipeline.examples.large import example_dataset


def main():
    with example_dataset(
        destination="combined", preview=DEBUG, encoding={VIDEO: {"zlib": True}}
    ) as ds:
        video = ds[VIDEO]
        maximum = video.max(FRAME)
        flooded: DA = apply_to_img_da(flood, maximum)
        roi = apply_to_img_da(close_and_erode, scale_bool(flooded))
        masked: DA = apply_to_img_da(apply_mask, video, scale_bool(roi), vectorize=True)
        binarized: DA = apply_to_img_da(binarize, masked, vectorize=True)
        ds[VIDEO] = pack(binarized)
        view_images(
            dict(
                video=video.isel(frame=0),
                maximum=maximum,
                flooded=flooded,
                roi=roi,
                masked=masked.isel(frame=0),
                binarized=binarized.isel(frame=0),
            )
        )


if __name__ == "__main__":
    main()
