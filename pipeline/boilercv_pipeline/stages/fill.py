"""Fill bubble contours."""

from loguru import logger
from tqdm import tqdm
from xarray import zeros_like

from boilercv.data import ROI, VIDEO
from boilercv.data.packing import pack
from boilercv.images import scale_bool
from boilercv.images.cv import draw_contours
from boilercv.types import ArrInt
from boilercv_pipeline.config import default
from boilercv_pipeline.sets import get_contours_df, get_dataset, process_datasets


def main():  # noqa: D103
    destination = default.params.paths.filled
    with process_datasets(destination) as videos_to_process:
        for name in tqdm(videos_to_process):
            df = get_contours_df(name)
            source_ds = get_dataset(name)
            ds = zeros_like(source_ds, dtype=source_ds[VIDEO].dtype)
            video = ds[VIDEO]
            if not df.empty:
                for frame_num, frame in enumerate(video):
                    contours: list[ArrInt] = list(  # pyright: ignore[reportAssignmentType]
                        df.loc[frame_num, :]
                        .groupby("contour")
                        .apply(lambda grp: grp.values)
                    )
                    video[frame_num, :, :] = draw_contours(
                        scale_bool(frame.values), contours
                    )
            ds[VIDEO] = pack(video)
            ds = ds.drop_vars(ROI)
            videos_to_process[name] = ds


if __name__ == "__main__":
    logger.info("Start filling contours")
    main()
    logger.info("Finish filling contours")
