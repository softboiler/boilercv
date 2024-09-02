"""Test `MorphMap`."""

from __future__ import annotations

from collections.abc import Callable, Mapping, MutableMapping
from contextlib import suppress
from typing import TYPE_CHECKING, Any, Generic, Literal, TypeAlias, TypeVar

import pytest
from pydantic import ValidationError

from boilercv.contexts.types import Context
from boilercv.morphs import Morph, TypeType

K = TypeVar("K")
"""Key type."""
V = TypeVar("V")
"""Value type."""

# fmt: off

# * MARK: Constants
Fruit: TypeAlias = Literal["apple", "banana", "cherry"]
ANY_MAP: dict[Any, Any] = {"any": "map"}
FRUIT: list[Fruit] = ["apple", "banana", "cherry"]
Str: TypeAlias = str | Context
Int: TypeAlias = int | Context
_SelfMap: TypeAlias = MutableMapping[Fruit, Str]
_SelfDict: TypeAlias = dict[Fruit, Str]
SELF_DICT: _SelfDict = {"apple": "delicious"}
_OtherDict: TypeAlias = dict[Fruit, Int]
OTHER_DICT: _OtherDict = dict.fromkeys(FRUIT, 0)

# * MARK: Concrete morphs

# ! Descriptions
Morph_: TypeAlias = Morph[Fruit, Str]
SELF_MORPH = Morph_(SELF_DICT)
class _Self(Morph_): ...
SELF = _Self(SELF_DICT)

# ! Counts
_OtherMorph: TypeAlias = Morph[Fruit, Int]
OTHER_MORPH = _OtherMorph(OTHER_DICT)
class _Other(_OtherMorph): ...
OTHER = _Other(OTHER_DICT)

# * MARK: Generic morphs and concrete morphs based on generic morph

# ! Note that `TypeAlias`es cannot be `Generic`, e.g. they don't support `TypeVar`s.
class _GenericMorph(Morph[K, V], Generic[K, V]): ...
GENERIC_MORPH = _GenericMorph[Any, Any](ANY_MAP)

# ! Descriptions
_SubSelfMorph: TypeAlias = _GenericMorph[Fruit, Str]
SUB_SELF_MORPH = _SubSelfMorph(SELF_DICT)
class _SubSelf(_SubSelfMorph): ...
SUB_SELF = _SubSelf(SELF_DICT)

# ! Counts
_SubOtherMorph: TypeAlias = _GenericMorph[Fruit, Int]
SUB_OTHER_MORPH = _SubOtherMorph(OTHER_DICT)
class _SubOther(_SubOtherMorph): ...
SUB_OTHER = _SubOther(OTHER_DICT)

# * MARK: ((Any -> Any) -> Any)

# ! (str -> UNANNOTATED)
def str_unk(i: str
    ): return len(i)
def _():
    return SELF.morph_pipe(str_unk)  # pyright: ignore[reportArgumentType, reportCallIssue]

# ! (str -> Any)
def str_any(i: str
    ) -> Any: return len(i)
def _():
    return SELF.morph_pipe(str_any)  # pyright: ignore[reportArgumentType, reportCallIssue]

# ! (str -> int)
def str_int(i: str
    ) -> int: return len(i)
def _():
    return SELF.morph_pipe(str_int)  # pyright: ignore[reportArgumentType, reportCallIssue]

# ! (str -> Map)
def str_map(i: str
    ) -> MutableMapping[str, Int]: return {i: len(i)}
def _():
    return SELF.morph_pipe(str_map)  # pyright: ignore[reportArgumentType, reportCallIssue]
def str_dict(_: str
    ) -> _SelfDict: return SELF_DICT
def _():
    return SELF.morph_pipe(str_dict)  # pyright: ignore[reportArgumentType, reportCallIssue]

# ! (str -> Morph)
def str_morph(_: str
    ) -> Morph_: return SELF_MORPH
def _():
    return SELF.morph_pipe(str_morph)  # pyright: ignore[reportArgumentType, reportCallIssue]

# ! (str -> Self)
def str_self(_: str
    ) -> _Self: return SELF
def _():
    return SELF.morph_pipe(str_self)  # pyright: ignore[reportArgumentType, reportCallIssue]

# * MARK: ((*[K2, V2] -> R) -> R)

# ! (UNANNOTATED -> str)
def unk_str(i
    ) -> str: return str(i)
def _():
    return SELF.morph_pipe(unk_str)

# ! (Any -> str)
def any_str(i: Any
    ) -> str: return str(i)
def _():
    return SELF.morph_pipe(any_str)

# ! (Map -> str)
def map_str(i: _SelfMap
    ) -> str: return str(i)
def _():
    return SELF.morph_pipe(map_str)

# ! (dict -> str)
def dict_str(i: _SelfDict
    ) -> str: return str(i)
def _():
    return SELF.morph_pipe(dict_str)

# ! (otherdict -> str)
def otherdict_str(i: _OtherDict
    ) -> str: return str(i)
def _():
    return SELF.morph_pipe(otherdict_str)  # pyright: ignore[reportArgumentType, reportCallIssue]

# ! (Morph -> str)
def morph_str(i: Morph_
    ) -> str: return str(i)
def _():
    return SELF.morph_pipe(morph_str)

# ! (Self -> str)
def self_str(i: _Self
    ) -> str: return str(i)
def _():
    return SELF.morph_pipe(self_str)

# ! Concrete subclasses are compatible with matching aliases, but not vice versa
def str_aliased_desc_2(_: str
    ) -> Morph_: return SELF
def _():
    return SELF.morph_pipe(str_aliased_desc_2)  # pyright: ignore[reportArgumentType, reportCallIssue]
def str_desc_2(_: str
    ) -> _Self: return SELF_MORPH  # pyright: ignore[reportReturnType]
def _():
    return SELF.morph_pipe(str_desc_2)  # pyright: ignore[reportArgumentType, reportCallIssue]

# * MARK: Define map-taking functions

# ! (Map -> Unk)
def map_unk(i: _SelfMap
    ): return Morph_(i)
def _():
    return SELF.morph_pipe(map_unk)
def dict_unk(i: dict[Fruit, Str]
    ): return Morph_(i)
def _():
    return SELF.morph_pipe(dict_unk)
def morph_unk(i: Morph_
    ): return Morph_(i)
def _():
    return SELF.morph_pipe(morph_unk)
def self_unk(i: _Self
    ): return i
def _():
    return SELF.morph_pipe(self_unk)

# ! (Map -> Any)
def map_any(i: _SelfMap
    ) -> Any: return Morph_(i)
def _():
    return SELF.morph_pipe(map_any)
def dict_any(i: dict[Fruit, Str]
    ) -> Any: return Morph_(i)
def _():
    return SELF.morph_pipe(dict_any)
def morph_any(i: Morph_
    ) -> Any: return Morph_(i)
def _():
    return SELF.morph_pipe(morph_any)
def self_any(i: _Self
    ) -> Any: return i
def _():
    return SELF.morph_pipe(self_any)

# ! (MutableMapping -> Morph)
def map_morph(i: _SelfMap
    ) -> Morph_: return Morph_(i)
def _():
    return SELF.morph_pipe(map_morph)
def map_self(i: _SelfMap
    ) -> _Self: return _Self(i)
def _():
    return SELF.morph_pipe(map_self)

# ! (dict -> Self)
def dict_morph(i: dict[Fruit, Str]
    ) -> Morph_: return Morph_(i)
def _():
    return SELF.morph_pipe(dict_morph)
def dict_self(i: dict[Fruit, Str]
    ) -> _Self: return _Self(i)
def _():
    return SELF.morph_pipe(dict_self)

# ! (Morph -> Self)
def morph_morph(i: Morph_
    ) -> Morph_: return Morph_(i)
def _():
    return SELF.morph_pipe(morph_morph)
def morph_self(i: Morph_
    ) -> _Self: return _Self(i)
def _():
    return SELF.morph_pipe(morph_self)

# ! (Self -> Self)
def self_self(i: _Self
    ) -> _Self: return i
def _():
    return SELF.morph_pipe(self_self)

# ! (Morph -> Other)
def morph1_self2(_: Morph_
    ) -> _Other: return OTHER
def _():
    return SELF.morph_pipe(morph1_self2)

# ! (Self -> Other)
def self1_self2(_: _Self
    ) -> _Other: return OTHER
def _():
    return SELF.morph_pipe(self1_self2)

# ! (Self -> Other)
def other_dict(_: _GenericMorph[Fruit, Int]
    ) -> _SelfDict: return SELF_DICT
def _():
    return SELF.morph_pipe(other_dict)  # pyright: ignore[reportArgumentType, reportCallIssue]

# * MARK: Key and value functions

def list_int_str(i: list[Fruit]) -> list[int]:
    return [len(j) for j in i]

def list_str_int(i: list[str]) -> list[int]:
    return [len(j) for j in i]

# fmt: on

# * MARK: Tests

Pipe: TypeAlias = TypeType[Any, Any, Any]
TakeStr: TypeAlias = Callable[[str], Any]
ReturnOther: TypeAlias = Callable[..., Any]
ReturnMatchingMap: TypeAlias = Callable[..., _SelfMap]
ReturnMismatchedMap: TypeAlias = Callable[..., Mapping[Any, Any]]
TakeFruitsReturnOther: TypeAlias = Callable[[list[Fruit]], Any]
TakeIntsReturnOther: TypeAlias = Callable[[list[str]], Any]
take_str: list[TakeStr] = [str_unk, str_any, str_int, str_map, str_self]
take_other_map: list[ReturnOther] = [otherdict_str, str_aliased_desc_2]
return_matching_maps: list[ReturnMatchingMap] = [
    str_dict,
    str_morph,
    str_desc_2,
    map_morph,
    map_self,
    dict_morph,
    dict_self,
    morph_morph,
    morph_self,
    self_self,
    other_dict,
]
return_mismatched_maps: list[ReturnMismatchedMap] = [
    map_any,
    dict_any,
    self_any,
    morph_any,
]
return_other_morph: list[ReturnMismatchedMap] = [morph1_self2, self1_self2]
take_fruits_return_other = [list_int_str]
take_strs_return_other = [list_str_int]

if TYPE_CHECKING:
    with suppress(TypeError, ValidationError):
        for f in take_str:
            v1 = SELF.morph_pipe(f)  # pyright: ignore[reportArgumentType, reportCallIssue]
        for f in take_other_map:
            v2 = SELF.morph_pipe(f)
        for f in return_matching_maps:
            v3 = SELF.morph_pipe(f)
        for f in return_mismatched_maps:
            v4 = SELF.morph_pipe(f)


@pytest.mark.parametrize("f", take_other_map)
def test_pipe_returns_other_from_not_mappings(f: Pipe):
    """Pipe produces other types from non-mappings."""
    assert SELF.morph_pipe(f) == f(SELF)


@pytest.mark.parametrize("f", return_matching_maps)
def test_pipe_returns_self_from_matching_map(f: Pipe):
    """Pipe produces matching mappings wrapped in instances of its class."""
    assert SELF.morph_pipe(f) == _Self(f(SELF))


@pytest.mark.parametrize("f", return_mismatched_maps)
def test_pipe_returns_base_from_mismatched_map(f: Pipe):
    """Pipe produces mismatched mappings wrapped in nearest instances."""
    result = SELF.morph_pipe(f)
    k, v = result.morph_get_inner_types()
    assert result == Morph[k, v](f(SELF))


@pytest.mark.parametrize("f", return_other_morph)
def test_pipe_returns_other_morph(f: Pipe):
    """Pipe produces other morphs."""
    result = SELF.morph_pipe(f)
    assert result == OTHER_MORPH
