"""Tests for experiment `e230920_subcool`."""

from os import environ
from pathlib import Path

import pytest
from dev.tests import Caser, parametrize_by_cases
from pandas.testing import assert_index_equal

pytestmark = [pytest.mark.slow, pytest.mark.skip(reason="Restructuring notebooks")]
C = Caser(Path("docs/experiments/e230920_subcool"))


@parametrize_by_cases(C("find_centers"))
def test_centers_index(ns):
    """Approaches have same centers index."""
    assert_index_equal(
        ns.trackpy_centers.columns,
        ns.centers.columns,
        check_order=False,  # pyright: ignore[reportCallIssue]
    )


@pytest.mark.xfail(
    raises=AssertionError,
    reason="Radius estimate cannot account for large and small bubbles alike",
)
@parametrize_by_cases(
    C("find_tracks_trackpy", "small_bubbles", {"TIME": "2023-09-20T17:14:18"})
)
def test_find_tracks_trackpy(ns, figs):
    """Small bubbles are tracked."""
    figs.extend(ns.figures)
    objects = ns.nondimensionalized_departing_long_lived_objects
    assert objects["Dimensionless bubble diameter"].min() < 0.2


@parametrize_by_cases(C("get_thermal_data"))
def test_get_thermal_data(ns):
    """Subcooling is as expected."""
    assert ns.data.subcool.mean() == pytest.approx(3.65, abs=0.01, rel=0.01)


@pytest.fixture(scope="module")
def nss(fixtures):
    """Namespaces from tests in this module."""
    return fixtures.ns.test_e230920_subcool


@pytest.mark.skipif(bool(environ.get("CI")), reason="CI")
def test_synthesis(nss, plt):
    """Synthesize results."""
    _, axes = plt.subplots(1, 3)
    axes = iter(axes)
    nss.test_centers_index._.centers.plot.scatter(ax=next(axes), x="x", y="y")
    nss.test_find_tracks_trackpy.small_bubbles.nondimensionalized_departing_long_lived_objects.plot.scatter(
        ax=next(axes), x="xpx", y="ypx"
    )
    nss.test_get_thermal_data._.data.plot(ax=next(axes))
