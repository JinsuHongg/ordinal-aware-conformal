"""Oracle local-path approximate ordinal borrowing primitives.

The directed adjacent-edge costs are structural assumptions supplied by the
caller.  This module neither estimates nor certifies them.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import ceil, inf
from typing import Sequence

import numpy as np

from .approximate_ordinal_borrowing import ordinal_neighborhood, population_mixture_weights


@dataclass(frozen=True)
class LocalPathCalibrationResult:
    thresholds: tuple[float, ...]
    ranks: tuple[int | None, ...]
    own_support: tuple[int, ...]
    pooled_support: tuple[int, ...]
    radii: tuple[int, ...]
    costs: tuple[float, ...]


def directed_path_cost(source: int, target: int, forward_edges: Sequence[float], backward_edges: Sequence[float]) -> float:
    """Cost along the directed ordinal path from ``source`` to ``target``."""
    if len(forward_edges) != len(backward_edges):
        raise ValueError("forward and backward edge vectors must have equal length")
    if not 0 <= source <= len(forward_edges) or not 0 <= target <= len(forward_edges):
        raise ValueError("class index out of range")
    if min(forward_edges, default=0.0) < 0 or min(backward_edges, default=0.0) < 0:
        raise ValueError("edge costs must be nonnegative")
    if source == target:
        return 0.0
    if source < target:
        return float(sum(forward_edges[source:target]))
    return float(sum(backward_edges[target:source]))


def path_borrowing_cost(probabilities: Sequence[float], class_id: int, radius: int, forward_edges: Sequence[float], backward_edges: Sequence[float]) -> float:
    """Population-mixture weighted directed path cost for one ordinal ball."""
    weights = population_mixture_weights(probabilities, class_id, radius)
    return float(sum(weight * directed_path_cost(source, class_id, forward_edges, backward_edges) for source, weight in enumerate(weights)))


def select_support_maximizing_radius(probabilities: Sequence[float], class_id: int, forward_edges: Sequence[float], backward_edges: Sequence[float], eta: float) -> tuple[int, float]:
    """Maximize population ball mass subject to a path-cost slack budget.

    Costs need not be monotone in radius because adding a class changes every
    conditional mixture weight.  The explicit support objective is therefore
    used instead of assuming the largest admissible radius is always optimal.
    """
    if eta < 0:
        raise ValueError("eta must be nonnegative")
    n_classes = len(probabilities)
    candidates = []
    for radius in range(max(class_id, n_classes - class_id - 1) + 1):
        cost = path_borrowing_cost(probabilities, class_id, radius, forward_edges, backward_edges)
        if cost <= eta + 1e-12:
            mass = sum(probabilities[index] for index in ordinal_neighborhood(class_id, radius, n_classes))
            candidates.append((mass, -radius, radius, cost))
    _, _, radius, cost = max(candidates)
    return radius, cost


def fit_local_path_approximate_borrowing(labels: Sequence[int], scores: Sequence[float], alpha: float, n_classes: int,
                                         probabilities: Sequence[float], forward_edges: Sequence[float], backward_edges: Sequence[float], eta: float) -> LocalPathCalibrationResult:
    """Pooled nominal split-conformal calibration using frozen oracle path costs."""
    label_values, score_values = np.asarray(labels, dtype=int), np.asarray(scores, dtype=float)
    thresholds: list[float] = []
    ranks: list[int | None] = []
    own_support: list[int] = []
    pooled_support: list[int] = []
    radii: list[int] = []
    costs: list[float] = []
    for class_id in range(n_classes):
        radius, cost = select_support_maximizing_radius(probabilities, class_id, forward_edges, backward_edges, eta)
        pooled = score_values[np.isin(label_values, list(ordinal_neighborhood(class_id, radius, n_classes)))]
        rank = ceil((len(pooled) + 1) * (1.0 - alpha))
        thresholds.append(inf if rank > len(pooled) else float(np.sort(pooled)[rank - 1]))
        ranks.append(None if rank > len(pooled) else rank)
        own_support.append(int(np.count_nonzero(label_values == class_id)))
        pooled_support.append(len(pooled)); radii.append(radius); costs.append(cost)
    return LocalPathCalibrationResult(tuple(thresholds), tuple(ranks), tuple(own_support), tuple(pooled_support), tuple(radii), tuple(costs))
