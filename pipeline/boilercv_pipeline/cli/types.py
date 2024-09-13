"""Types."""

from typing import TypeVar

from pydantic import BaseModel

Model_T = TypeVar("Model_T", bound=BaseModel)
