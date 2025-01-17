"""Tests for experiment `e230920_subcool`."""

from os import environ
from pathlib import Path

import pytest
from boilercv_dev.tests import Caser, parametrize_by_cases

pytestmark = pytest.mark.slow
C = Caser(Path("docs") / "notebooks")


# TODO: Fix permission error for test running in CI
@pytest.mark.skipif(bool(environ.get("CI")), reason="Unresolved permission error.")
@parametrize_by_cases(C("find_objects"))
def test_approaches_close(ns):
    """Object-finding approaches have similar object counts."""
    tp = len(ns.trackpy_preview)
    cen = len(ns.centroids_preview)
    assert (abs(tp - cen) / cen) < 10


@pytest.fixture(scope="module")
def nss(fixtures):
    """Namespaces from tests in this module."""
    return fixtures.ns.test_subcool


@pytest.mark.skipif(bool(environ.get("CI")), reason="For local inspection only.")
def test_synthesis(nss, request):
    """Synthesize results."""
    plots = Path(request.config.option.plots)
    plots.mkdir(parents=True, exist_ok=True)
    nss.test_approaches_close._.data.plots.composite.savefig(
        plots / "test_approaches_close_composite.png"
    )
