"""Tests."""

from collections.abc import Callable

import pytest


@pytest.mark.slow
def test_stages(stage: Callable[[], None]):
    """Test that stages can run."""
    stage()
