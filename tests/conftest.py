"""Test configuration."""

import pickle
from collections import defaultdict
from collections.abc import Iterator
from dataclasses import dataclass
from functools import partial
from importlib import import_module
from logging import warning
from os import environ, getpid
from pathlib import Path
from re import fullmatch
from shutil import copy, rmtree
from types import SimpleNamespace

import pytest
import pytest_harvest
from _pytest.python import Function
from boilercore.notebooks.namespaces import get_nb_ns, get_ns_attrs
from boilercore.warnings import WarningFilter
from boilercv_dev.tests import Case, get_cached_nb_ns
from boilercv_dev.tests.config import const
from boilercv_dev.tests.types import FixtureStore
from boilercv_dev.tools.warnings import filter_boilercv_warnings
from boilercv_pipeline.config import const as boilercv_pipeline_const
from boilercv_pipeline.models.contexts import Roots
from boilercv_pipeline.models.path import get_boilercv_pipeline_context
from context_models import CONTEXT
from matplotlib.axis import Axis
from matplotlib.figure import Figure
from pydantic.alias_generators import to_pascal

CASER = "C"
"""Module-level variable in test modules containing notebook cases for that module."""

# * MARK: Autouse


@pytest.fixture(autouse=True, scope="session")
def _filter_certain_warnings():
    """Filter certain warnings."""
    filter_boilercv_warnings(other_warnings_before=[WarningFilter(action="error")])


@pytest.fixture(scope="module", autouse=True)
def _get_ns_attrs(request):
    module = request.module
    caser = getattr(module, CASER, None)
    if not caser:
        yield
        return
    cases = caser.cases
    notebook_namespace_tests = (
        node
        for node in request.node.collect()
        if isinstance(node, Function) and "ns" in node.fixturenames
    )
    for case, test in zip(cases, notebook_namespace_tests, strict=True):
        name = getattr(module, test.originalname)
        case.results = sorted(set(case.results) | set(get_ns_attrs(name)))
    yield
    for nb in [c.clean_path for c in cases if c.clean_path]:
        nb.unlink(missing_ok=True)


# * MARK: Notebook namespaces


def get_params(stage: str, tmp: Path, **kwds):
    """Get stage parameters."""
    if not environ.get("CI"):
        for path in const.data.glob("uncompressed_*"):
            rmtree(path)
    (tmp_e230920 := tmp / "e230920").mkdir(parents=True, exist_ok=True)
    copy(const.data / "e230920" / "thermal.h5", tmp_e230920)
    module = f"boilercv_pipeline.stages.{stage}"
    Params = getattr(import_module(module), f"{to_pascal(stage)}")  # noqa: N806
    fields = Params.model_fields
    return Params(**{
        CONTEXT: get_boilercv_pipeline_context(
            Roots(data=const.data, docs=boilercv_pipeline_const.docs)
        ),
        "outs": {
            CONTEXT: get_boilercv_pipeline_context(
                Roots(data=tmp, docs=boilercv_pipeline_const.docs)
            )
        },
        **({"only_sample": True} if "only_sample" in fields else {}),
        **({"load_src_from_outs": True} if "load_src_from_outs" in fields else {}),
        **kwds,
    })


@pytest.fixture(params=boilercv_pipeline_const.stages)
def stage(tmp_path, request):
    """Pipeline stage."""
    stage: str = request.param
    module = f"boilercv_pipeline.stages.{stage}"
    return partial(
        import_module(f"{module}.__main__").main, get_params(stage, tmp_path)
    )


@pytest.fixture
@pytest_harvest.saved_fixture
def ns(tmp_path, request, fixture_stores) -> Iterator[SimpleNamespace]:
    """Notebook stage namespace."""
    case: Case = request.param
    params = {
        "PARAMS": (
            get_params(case.stage, tmp_path, **case.params) if case.params else None
        ),
        "MODE": "docs",
    }
    attributes = ["params", "data", *case.results]
    if environ.get("CI"):
        yield get_nb_ns(nb=case.nb, params=params, attributes=attributes)
        return
    yield get_cached_nb_ns(nb=case.clean_nb(), params=params, attributes=attributes)
    update_fixture_stores(
        fixture_stores,
        request.fixturename,
        test=request.node.name,
        path=request.node.path,
    )


# * MARK: Harvest


@dataclass
class FixtureStores:
    """Fixture stores from `pytest-harvest`."""

    flat: FixtureStore
    """The default flat fixture store from `pytest-harvest`."""
    nested: FixtureStore
    """Fixture for test cases, nested by fixture name, module, then node."""


def update_fixture_stores(
    fixture_stores: FixtureStores, fixturename: str, test: str, path: Path
):
    """Update nested fixture store with the new namespace."""
    module = fixture_stores.nested[fixturename][
        path.relative_to(Path("tests").resolve()).with_suffix("").as_posix()
    ]
    # Pattern for e.g. `test[case]`
    if match := fullmatch(pattern=r"(?P<node>[^\[]+)\[(?P<case>[^\]]+)\]", string=test):
        node, case = match.groups()
        key = f"{path.relative_to(Path.cwd()).as_posix()}::{test}"
        module[node][case] = fixture_stores.flat[fixturename][key]


@pytest.fixture(scope="session")
def fixtures(nested_fixture_store) -> SimpleNamespace:
    """Fixtures from `pytest-harvest`."""
    return SimpleNamespace(**{
        key: SimpleNamespace(**{
            key: SimpleNamespace(**{
                key: SimpleNamespace(**value) for key, value in value.items()
            })
            for key, value in value.items()
        })
        for key, value in nested_fixture_store.items()
    })


@pytest.fixture(scope="session")
def nested_fixture_store(fixture_stores) -> FixtureStore:
    """Nested fixture store."""
    return fixture_stores.nested


@pytest.fixture(scope="session")
def fixture_stores(fixture_store) -> FixtureStores:
    """Flat fixture store from `pytest-harvest` and nested fixture store."""
    return FixtureStores(
        flat=fixture_store,
        nested=defaultdict(
            lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
        ),
    )


# * MARK: Plotting


@pytest.fixture
def figs(request, pytestconfig) -> Iterator[list[Figure]]:
    """Append to this list of Matplotlib figures to save them after the test run."""
    plots = Path(pytestconfig.option.plots)
    plots.mkdir(parents=True, exist_ok=True)
    path = plots / f"{request.node.nodeid.replace('/', '.').replace(':', '-')}.png"
    figs = []
    yield figs
    path.unlink(missing_ok=True)
    figs = iter(figs)
    if first_fig := next(figs, None):
        first_fig.savefig(path)
    for i, fig in enumerate(figs):
        path = path.with_stem(f"{path.stem}_{i}")
        path.unlink(missing_ok=True)
        fig.savefig(path)


@pytest.fixture
def plt(plt):
    """Plot."""
    yield plt
    plt.saveas = f"{plt.saveas[:-4]}.png"


@pytest.fixture
def fig_ax(plt) -> tuple[Figure, Axis]:
    """Plot figure and axis."""
    fig, ax = plt.subplots()
    return fig, ax


@pytest.fixture
def fig(fig_ax) -> Figure:
    """Plot figure."""
    return fig_ax[0]


@pytest.fixture
def ax(fig_ax) -> Axis:
    """Plot axis."""
    return fig_ax[1]


# * MARK: Harvest hooks
# * https://github.com/smarie/python-pytest-harvest/issues/46#issuecomment-742367746
# * https://smarie.github.io/python-pytest-harvest/#pytest-x-dist

HARVEST_ROOT = Path(".xdist_harvested")
"""Root directory for harvested results."""
RESULTS_PATH = HARVEST_ROOT / str(getpid())
"""Path to harvested results for a given `pytest-xdist` subprocess."""

HARVEST_ROOT.mkdir(exist_ok=True)
RESULTS_PATH.mkdir(exist_ok=True)


def pytest_harvest_xdist_init():
    """Reset the recipient folder."""
    rmtree(RESULTS_PATH, ignore_errors=True)
    RESULTS_PATH.mkdir(exist_ok=False)
    return True


def pytest_harvest_xdist_worker_dump(worker_id, session_items, fixture_store):
    """Persist session_items and fixture_store in the file system."""
    with (RESULTS_PATH / f"{worker_id}.pkl").open("wb") as f:
        try:
            pickle.dump((session_items, fixture_store), f)
        except Exception as e:
            warning(
                "Error while pickling worker %s's harvested results: [%s] %s",
                (worker_id, e.__class__, e),
            )
    return True


def pytest_harvest_xdist_load():
    """Restore the saved objects from file system."""
    workers_saved_material = {}
    for pkl_file in sorted(RESULTS_PATH.glob("*.pkl")):
        wid = pkl_file.stem
        with pkl_file.open("rb") as f:
            workers_saved_material[wid] = pickle.load(f)
    return workers_saved_material


def pytest_harvest_xdist_cleanup():
    """Don't clean up. Fails to delete directories often."""
    return True
