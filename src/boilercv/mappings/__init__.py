"""Mapping functions."""

from collections.abc import Callable, Iterable, Mapping, MutableMapping
from copy import copy
from re import Pattern, sub
from typing import Any, Generic, NamedTuple

from boilercv.mappings.types import MN, SK, K, Leaf, MutableNode_T, Node, T, V


def apply(
    mapping: Mapping[K, V],
    skip_key: Callable[[Any], bool] = lambda _: False,
    node_fun_pre: Callable[[Node], Any] = lambda n: n,
    skip_node: Callable[[Node], bool] = lambda _: False,
    del_node_pre: Callable[[Node], bool] = lambda _: False,
    node_fun: Callable[[Node], Any] = lambda n: n,
    del_node: Callable[[Node], bool] = lambda _: False,
    leaf_fun_pre: Callable[[Leaf], Any] = lambda v: v,
    skip_leaf: Callable[[Leaf], bool] = lambda _: False,
    del_leaf_pre: Callable[[Leaf], bool] = lambda _: False,
    leaf_fun: Callable[[Leaf], Any] = lambda v: v,
    del_leaf: Callable[[Leaf], bool] = lambda _: False,
) -> dict[K, V]:
    """Apply functions conditionally to nodes and leaves of a mapping."""
    return update(
        mapping=dict(copy(mapping)),
        skip_key=skip_key,
        node_fun_pre=lambda n: node_fun_pre(copy(n)),
        skip_node=skip_node,
        del_node_pre=del_node_pre,
        node_fun=node_fun,
        del_node=del_node,
        leaf_fun_pre=lambda v: leaf_fun_pre(copy(v)),
        skip_leaf=skip_leaf,
        del_leaf_pre=del_leaf_pre,
        leaf_fun=leaf_fun,
        del_leaf=del_leaf,
    )


def update(  # noqa: C901
    mapping: MutableNode_T,
    skip_key: Callable[[Any], bool] = lambda _: False,
    node_fun_pre: Callable[[MutableNode_T], Any] = lambda n: n,
    skip_node: Callable[[MutableNode_T], bool] = lambda _: False,
    del_node_pre: Callable[[MutableNode_T], bool] = lambda _: False,
    node_fun: Callable[[MutableNode_T], Any] = lambda n: n,
    del_node: Callable[[MutableNode_T], bool] = lambda _: False,
    leaf_fun_pre: Callable[[Leaf], Any] = lambda v: v,
    skip_leaf: Callable[[Leaf], bool] = lambda _: False,
    del_leaf_pre: Callable[[Leaf], bool] = lambda _: False,
    leaf_fun: Callable[[Leaf], Any] = lambda v: v,
    del_leaf: Callable[[Leaf], bool] = lambda _: False,
) -> MutableNode_T:
    """Update in-place by applying functions conditionally to nodes and leaves."""
    # ? `deepcopy` is wasteful and has side-effects on some leaves (e.g. SymPy exprs)
    # ? Instead, `copy` mappings on entry and `copy` leaves before applying `leaf_fun`
    marks: list[Any] = []
    for key, value in mapping.items():
        if skip_key(key):
            continue
        if isinstance(node := value, Mapping):
            mapping[key] = node = node_fun_pre(node)  # pyright: ignore[reportArgumentType]
            if skip_node(node):
                continue
            if del_node_pre(node):
                marks.append(key)
                continue
            mapping[key] = node = node_fun(
                update(
                    mapping=node,
                    skip_key=skip_key,
                    node_fun_pre=node_fun_pre,
                    skip_node=skip_node,
                    del_node_pre=del_node_pre,
                    node_fun=node_fun,
                    del_node=del_node,
                    leaf_fun_pre=leaf_fun_pre,
                    skip_leaf=skip_leaf,
                    del_leaf_pre=del_leaf_pre,
                    leaf_fun=leaf_fun,
                    del_leaf=del_leaf,
                )
            )
            if del_node(node):
                marks.append(key)
            continue
        leaf = value
        mapping[key] = leaf = leaf_fun_pre(leaf)
        if skip_leaf(leaf):
            continue
        if del_leaf_pre(leaf):
            marks.append(key)
            continue
        mapping[key] = leaf_fun(leaf)
        if del_leaf(leaf):
            marks.append(key)
            continue
    for mark in marks:
        del mapping[mark]
    return mapping


def is_falsey(v: Any) -> bool:
    """Check if a value is falsey, handling array types."""
    return not (v.any() if getattr(v, "any", None) else v)


def filt(mapping: Mapping[K, V]) -> dict[K, V]:
    """Filter nodes and leaves of a mapping recursively."""
    return apply(mapping, del_node=is_falsey, del_leaf=is_falsey)


def sort_by_keys_pattern(
    mapping: Mapping[SK, V],
    /,
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

    return dict(sorted(mapping.items(), key=get_key))


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


def replace(
    mapping: MutableMapping[K, str], /, repls: Iterable[Repl[K]]
) -> dict[K, str]:
    """Make replacements from `Repl`s."""
    for r in repls:
        mapping[r.dst] = mapping[r.src].replace(r.find, r.repl)
    return dict(mapping)


def replace_pattern(
    mapping: MutableMapping[K, str], /, repls: Iterable[Repl[K]]
) -> dict[K, str]:
    """Make regex replacements."""
    for r in repls:
        mapping[r.dst] = sub(r.find, r.repl, mapping[r.src])
    return dict(mapping)


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
