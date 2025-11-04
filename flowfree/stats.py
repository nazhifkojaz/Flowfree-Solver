from copy import deepcopy
from collections.abc import Iterable, Mapping
from typing import Any

BASE_SCHEMA: dict[str, Any] = {
    "time_s": 0.0,
    "attempts": 0,
    "backtracks": 0,
    "decision_nodes": 0,
    "total_branching": 0,
    "max_branching": 0,
    "tree_depth": 0,
    "nodes_generated": 0,
}


def new_stats(extra: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """
    Return a fresh stats dictionary that contains the canonical base schema plus any
    optional metrics provided in ``extra``.
    """
    stats = deepcopy(BASE_SCHEMA)
    if extra:
        stats.update(extra)
    return stats


def ensure_keys(stats: dict[str, Any], keys: Iterable[str]) -> None:
    """
    Guarantee that ``stats`` contains zero-initialized entries for each key in ``keys``.
    Useful for optional metric families that may not be touched during a solve.
    """
    for key in keys:
        stats.setdefault(key, 0)


def bump(stats: dict[str, Any], key: str, amount: int = 1) -> None:
    """Increment ``stats[key]`` by ``amount`` while keeping zero default."""
    stats[key] = stats.get(key, 0) + amount


def bump_propagation(stats: dict[str, Any], name: str, amount: int = 1) -> None:
    """
    Increment an individual propagation counter using the standard
    ``propagations_<name>`` naming convention.
    """
    bump(stats, f"propagations_{name}", amount)
