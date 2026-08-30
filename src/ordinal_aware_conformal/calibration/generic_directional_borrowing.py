"""Oracle generic directional borrowing for the local-path novelty stress test."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import ceil, inf
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class GenericCalibrationResult:
    thresholds: tuple[float, ...]
    ranks: tuple[int | None, ...]
    own_support: tuple[int, ...]
    pooled_support: tuple[int, ...]
    groups: tuple[tuple[int, ...], ...]
    costs: tuple[float, ...]


def subsets_containing_target(n_classes: int, target: int) -> tuple[tuple[int, ...], ...]:
    """Enumerate every subset containing ``target`` exactly once."""
    other = [index for index in range(n_classes) if index != target]
    groups = []
    for size in range(len(other) + 1):
        for selected in combinations(other, size):
            groups.append(tuple(sorted((target, *selected))))
    return tuple(groups)


def direct_directional_cost(probabilities: Sequence[float], target: int, group: Sequence[int], directional: Sequence[Sequence[float]]) -> float:
    """Mixture-weighted direct directional discrepancy for an arbitrary group."""
    members = tuple(sorted(set(group)))
    if target not in members:
        raise ValueError("group must contain target")
    mass = sum(probabilities[index] for index in members)
    if mass <= 0:
        raise ValueError("group must have positive population mass")
    return float(sum(probabilities[index] / mass * directional[index][target] for index in members))


def is_contiguous(group: Sequence[int]) -> bool:
    values = tuple(sorted(set(group)))
    return values == tuple(range(values[0], values[-1] + 1))


def is_ordinal_ball(group: Sequence[int], target: int, n_classes: int) -> bool:
    values = tuple(sorted(set(group)))
    for radius in range(max(target, n_classes - target - 1) + 1):
        candidate = tuple(range(max(0, target - radius), min(n_classes, target + radius + 1)))
        if values == candidate:
            return True
    return False


def select_generic_group(probabilities: Sequence[float], target: int, directional: Sequence[Sequence[float]], eta: float) -> tuple[tuple[int, ...], float]:
    """Maximize population mass under the exact direct directional slack cost."""
    candidates = []
    for group in subsets_containing_target(len(probabilities), target):
        cost = direct_directional_cost(probabilities, target, group, directional)
        if cost <= eta + 1e-12:
            # Lexicographic group tie break is deterministic and independent of
            # calibration scores.
            candidates.append((sum(probabilities[index] for index in group), tuple(-index for index in group), group, cost))
    _, _, group, cost = max(candidates)
    return group, cost


def fit_generic_directional_borrowing(labels: Sequence[int], scores: Sequence[float], alpha: float, n_classes: int,
                                      probabilities: Sequence[float], directional: Sequence[Sequence[float]], eta: float) -> GenericCalibrationResult:
    """Nominal pooled conformal calibration for frozen arbitrary oracle groups."""
    label_values, score_values = np.asarray(labels, dtype=int), np.asarray(scores, dtype=float)
    thresholds: list[float] = []
    ranks: list[int | None] = []
    own_support: list[int] = []
    pooled_support: list[int] = []
    groups: list[tuple[int, ...]] = []
    costs: list[float] = []
    for target in range(n_classes):
        group, cost = select_generic_group(probabilities, target, directional, eta)
        pooled = score_values[np.isin(label_values, group)]
        rank = ceil((len(pooled) + 1) * (1.0 - alpha))
        thresholds.append(inf if rank > len(pooled) else float(np.sort(pooled)[rank - 1]))
        ranks.append(None if rank > len(pooled) else rank)
        own_support.append(int(np.count_nonzero(label_values == target)))
        pooled_support.append(len(pooled)); groups.append(group); costs.append(cost)
    return GenericCalibrationResult(tuple(thresholds), tuple(ranks), tuple(own_support), tuple(pooled_support), tuple(groups), tuple(costs))
