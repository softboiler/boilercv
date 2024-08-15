"""Run examples for the `boilercv.previews` module."""

from pathlib import Path

from boilercv.types import DA
from boilercv_pipeline import PREVIEW, WRITE, run_example
from boilercv_pipeline.captivate import FRAMERATE_PREV
from boilercv_pipeline.captivate.captures import write_video
from boilercv_pipeline.captivate.previews import view_images
from boilercv_pipeline.models.paths import paths
from boilercv_pipeline.previews.binarized import main as main2
from boilercv_pipeline.previews.composite import main as main3
from boilercv_pipeline.previews.filled import main as main4
from boilercv_pipeline.previews.gray import main as main1

results: dict[str, DA] = {}

for func in (main1, main2, main3, main4):
    module_name, result = run_example(func)
    results[module_name] = result
    if WRITE:
        module_path = Path(module_name.replace(".", "/").removeprefix("boilercv/"))
        path = paths.media / module_path
        path.parent.mkdir(parents=True, exist_ok=True)
        write_video(path, result, framerate=FRAMERATE_PREV)

if PREVIEW:
    view_images(results, framerate=FRAMERATE_PREV)
