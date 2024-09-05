"""Notebook operations."""

from collections.abc import Callable, Iterable
from concurrent.futures import Future, ProcessPoolExecutor
from typing import Any

from boilercore.notebooks.namespaces import get_nb_ns

from boilercv_pipeline.models.params import DataParams
from boilercv_pipeline.models.params.types import Data_T
from boilercv_pipeline.models.stage import StagePaths


def apply_to_nb(
    nb: str, params: DataParams[StagePaths, StagePaths, Data_T], **kwds: Any
) -> Data_T:
    """Apply a process to a notebook."""
    return get_nb_ns(
        nb=nb, params={"PARAMS": params.model_dump_json(), **kwds}
    ).params.data


def submit_nb_process(
    executor: ProcessPoolExecutor,
    nb: str,
    params: DataParams[StagePaths, StagePaths, Data_T],
    **kwds: Any,
) -> Future[Data_T]:
    """Submit a notebook process to an executor."""
    return executor.submit(apply_to_nb, nb=nb, params=params, **kwds)


def callbacks(
    future: Future[Data_T], /, callbacks: Iterable[Callable[[Future[Data_T]], None]]
):
    """Apply a series of done callbacks to the future."""
    for callback in callbacks:
        callback(future)
