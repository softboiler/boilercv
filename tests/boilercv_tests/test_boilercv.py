"""Tests."""

from importlib import import_module

import pytest

from boilercv_tests import STAGES


@pytest.mark.slow
@pytest.mark.parametrize("stage", STAGES)
def test_stages(stage: str):
    """Test that stages can run."""
    import_module(stage).main()
