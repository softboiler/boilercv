"""Mapping functions."""

from collections.abc import Callable, Iterable, Mapping, MutableMapping
from copy import deepcopy
from re import sub
from typing import TYPE_CHECKING, Any, TypeVar

from boilercv.mappings.models import Repl
from boilercv.mappings.types import K, Leaf, MutableNode, Node

if TYPE_CHECKING:
    from boilercv.mappings.models import Repl


def filt(
    mapping: Mapping[Any, Any],
    node_cond: Callable[[Node], bool] = bool,
    leaf_cond: Callable[[Node], bool] = bool,
) -> dict[Any, Any]:
    """Filter nodes and leaves of a mapping recursively."""
    return apply(mapping, node_cond=node_cond, leaf_cond=leaf_cond)


def apply(
    mapping: Mapping[Any, Any],
    node_fun: Callable[[Node], Any] = lambda n: n,
    leaf_fun: Callable[[Leaf], Any] = lambda v: v,
    node_cond: Callable[[Node], bool] = bool,
    leaf_cond: Callable[[Node], bool] = bool,
) -> dict[Any, Any]:
    """Apply functions and conditions recursively to nodes and leaves of a mapping."""
    filtered = dict(deepcopy(mapping))
    marks: list[Any] = []
    for key in filtered:
        if isinstance(filtered[key], Mapping):
            filtered[key] = apply(filtered[key], node_fun, leaf_fun)
            filtered[key] = node_fun(filtered[key])
            if not node_cond(filtered[key]):
                marks.append(key)
            continue
        filtered[key] = leaf_fun(filtered[key])
        if not leaf_cond(filtered[key]):
            marks.append(key)
    for mark in marks:
        del filtered[mark]
    return filtered


MutableNode_T = TypeVar("MutableNode_T", bound=MutableNode)


def sync(reference: Node | Leaf, target: MutableNode_T | Leaf) -> MutableNode_T:
    """Sync two mappings."""
    synced = deepcopy(target)
    for key in [k for k in synced if k not in reference]:
        del synced[key]
    for key in reference:
        if key in synced:
            if reference[key] == synced[key]:
                continue
            if isinstance(reference[key], dict) and isinstance(
                synced[key], MutableMapping
            ):
                sync(reference[key], synced[key])
                continue
        synced[key] = reference[key]
    return synced


def write(self) -> None:
    """Write to TOML."""
    self.path.write_text(self.sync().as_string(), "utf-8")


def replace(i: dict[K, str], repls: Iterable[Repl[K]]) -> dict[K, str]:
    """Make replacements from `Repl`s."""
    for r in repls:
        i[r.dst] = i[r.src].replace(r.find, r.repl)
    return dict(i)


def regex_replace(i: dict[K, str], repls: Iterable[Repl[K]]) -> dict[K, str]:
    """Make regex replacements."""
    for r in repls:
        i[r.dst] = sub(r.find, r.repl, i[r.src])
    return i
