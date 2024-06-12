"""Mapping functions."""

from collections.abc import Callable, Iterable, Mapping, MutableMapping
from copy import deepcopy
from re import Pattern, sub
from typing import Any, Generic, NamedTuple

from boilercv.mappings.types import MN, SK, K, Leaf, Node, T, V


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


def filt(
    mapping: Mapping[Any, Any],
    node_cond: Callable[[Node], bool] = bool,
    leaf_cond: Callable[[Node], bool] = bool,
) -> dict[Any, Any]:
    """Filter nodes and leaves of a mapping recursively."""
    return apply(mapping, node_cond=node_cond, leaf_cond=leaf_cond)


def sort_by_keys_pattern(
    i: Mapping[SK, V],
    pattern: Pattern[str],
    groups: Iterable[str],
    apply_to_match: Callable[[list[str]], Any] = str,
    message: str = "Match not found when sorting.",
) -> dict[SK, V]:
    """Sort mapping by named grouping in keys pattern."""

    def get_key(item: tuple[str, Any]) -> str:
        if match := pattern.search(key := item[0]):
            return apply_to_match([match[g] for g in groups])
        raise ValueError(message.format(key=key))

    return dict(sorted(i.items(), key=get_key))


class Repl(NamedTuple, Generic[T]):
    """Contents of `dst` to replace with `src`, with `find` substrings replaced with `repl`."""

    src: T
    """Source identifier."""
    dst: T
    """Destination identifier."""
    find: str
    """Find this in the source."""
    repl: str
    """Replacement for what was found."""


def replace(i: dict[K, str], repls: Iterable[Repl[K]]) -> dict[K, str]:
    """Make replacements from `Repl`s."""
    for r in repls:
        i[r.dst] = i[r.src].replace(r.find, r.repl)
    return dict(i)


def replace_pattern(i: dict[K, str], repls: Iterable[Repl[K]]) -> dict[K, str]:
    """Make regex replacements."""
    for r in repls:
        i[r.dst] = sub(r.find, r.repl, i[r.src])
    return i


def sync(reference: Node | Leaf, target: MN | Leaf) -> MN:
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
                synced[key] = sync(reference[key], synced[key])
                continue
        synced[key] = reference[key]
    return synced
