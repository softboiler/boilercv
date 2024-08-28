"""Mapping functions."""

from collections.abc import Callable, Iterable, Mapping, MutableMapping
from copy import copy
from re import Pattern, sub
from typing import Any, Generic, NamedTuple

from boilercv.mappings.types import MN, SK, K, Leaf, Node, T, V


def apply(
    mapping: Mapping[Any, Any],
    node_fun: Callable[[Node], Any] = lambda n: n,
    leaf_fun: Callable[[Leaf], Any] = lambda v: v,
    key_cond: Callable[[Any], bool] = lambda _: True,
    node_cond_before: Callable[[Node], bool] = lambda _: True,
    node_cond_after: Callable[[Node], bool] = lambda _: True,
    leaf_cond_before: Callable[[Node], bool] = lambda _: True,
    leaf_cond_after: Callable[[Node], bool] = lambda _: True,
) -> dict[Any, Any]:
    """Apply functions and conditions recursively to nodes and leaves of a mapping."""
    # ? `deepcopy` is wasteful and has side-effects on some leaves (e.g. SymPy exprs)
    # ? Instead, `copy` mappings on entry and `copy` leaves before applying `leaf_fun`
    filtered = dict(copy(mapping))
    marks: list[Any] = []
    for k, v in filtered.items():
        if not key_cond(k):
            continue
        if isinstance(v, Mapping):
            if not node_cond_before(v):
                continue
            filtered[k] = node_fun(
                apply(
                    mapping=filtered[k],
                    node_fun=node_fun,
                    leaf_fun=leaf_fun,
                    key_cond=key_cond,
                    node_cond_before=node_cond_before,
                    node_cond_after=node_cond_after,
                    leaf_cond_before=leaf_cond_before,
                    leaf_cond_after=leaf_cond_after,
                )
            )
            if not node_cond_after(filtered[k]):
                marks.append(k)
            continue
        if not leaf_cond_before(v):
            continue
        filtered[k] = leaf_fun(copy(filtered[k]))
        if not leaf_cond_after(filtered[k]):
            marks.append(k)
    for mark in marks:
        del filtered[mark]
    return filtered


def is_truthy(v: Any) -> bool:
    """Check if a value is truthy, handling array types."""
    return v.any() if getattr(v, "any", None) else bool(v)


def filt(
    mapping: Mapping[Any, Any],
    node_cond: Callable[[Node], bool] = is_truthy,
    leaf_cond: Callable[[Node], bool] = is_truthy,
) -> dict[Any, Any]:
    """Filter nodes and leaves of a mapping recursively."""
    return apply(mapping, node_cond_after=node_cond, leaf_cond_after=leaf_cond)


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
    # ? `deepcopy` is wasteful and has side-effects on some leaves (e.g. SymPy exprs)
    # ? Instead, `copy` target on entry
    synced = copy(target)
    for key in [k for k in synced if k not in reference]:
        del synced[key]
    for key in reference:
        if key in synced:
            if reference[key] == synced[key]:
                continue
            if isinstance(reference[key], Mapping) and isinstance(
                synced[key], MutableMapping
            ):
                synced[key] = sync(reference[key], synced[key])
                continue
        synced[key] = reference[key]
    return synced
