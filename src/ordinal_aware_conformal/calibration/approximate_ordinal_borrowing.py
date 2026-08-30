"""Approximate ordinal class-conditional calibration under a fixed assumption.

This exploratory rule makes the coverage cost of ordinal pooling explicit.  It
does not estimate or certify the directional smoothness constant; callers must
supply it as an externally justified structural assumption.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import ceil, inf
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class ApproximateCalibrationResult:
    thresholds: tuple[float, ...]
    ranks: tuple[int | None, ...]
    own_support: tuple[int, ...]
    pooled_support: tuple[int, ...]
    radii: tuple[int, ...]
    costs: tuple[float, ...]


def ordinal_neighborhood(class_id: int, radius: int, n_classes: int) -> range:
    return range(max(0, class_id - radius), min(n_classes, class_id + radius + 1))


def population_mixture_weights(probabilities: Sequence[float], class_id: int, radius: int) -> tuple[float, ...]:
    """Population, not realized calibration, mixture weights for one ball."""
    values = np.asarray(probabilities, dtype=float)
    if np.any(values < 0) or not np.isclose(values.sum(), 1.0):
        raise ValueError("probabilities must be nonnegative and sum to one")
    neighborhood = ordinal_neighborhood(class_id, radius, len(values))
    mass = float(values[list(neighborhood)].sum())
    if mass == 0.0:
        raise ValueError("neighborhood must have positive population mass")
    return tuple(float(values[index] / mass) if index in neighborhood else 0.0 for index in range(len(values)))


def borrowing_cost(probabilities: Sequence[float], class_id: int, radius: int, lipschitz_constant: float) -> float:
    """Mixture-weighted directional borrowing cost \(L\sum_j\rho_{kj}|j-k|\)."""
    if lipschitz_constant < 0:
        raise ValueError("lipschitz_constant must be nonnegative")
    weights = population_mixture_weights(probabilities, class_id, radius)
    return float(lipschitz_constant * sum(weight * abs(index - class_id) for index, weight in enumerate(weights)))


def worst_case_borrowing_cost(radius: int, lipschitz_constant: float) -> float:
    return float(lipschitz_constant * radius)


def select_largest_admissible_radius(probabilities: Sequence[float], class_id: int, lipschitz_constant: float, eta: float,
                                     weighted: bool = True) -> tuple[int, float]:
    """Select the largest ordinal ball satisfying the pre-specified slack budget."""
    if eta < 0:
        raise ValueError("eta must be nonnegative")
    n_classes = len(probabilities)
    admissible = []
    for radius in range(max(class_id, n_classes - class_id - 1) + 1):
        cost = borrowing_cost(probabilities, class_id, radius, lipschitz_constant) if weighted else worst_case_borrowing_cost(radius, lipschitz_constant)
        if cost <= eta + 1e-12:
            admissible.append((radius, cost))
    return max(admissible, key=lambda item: item[0])


def fit_approximate_ordinal_borrowing(labels: Sequence[int], scores: Sequence[float], alpha: float, n_classes: int,
                                      probabilities: Sequence[float], lipschitz_constant: float, eta: float,
                                      weighted: bool = True) -> ApproximateCalibrationResult:
    """Pool each frozen slack-admissible neighborhood at nominal conformal rank."""
    label_values, score_values = np.asarray(labels, dtype=int), np.asarray(scores, dtype=float)
    thresholds: list[float] = []
    ranks: list[int | None] = []
    own_support: list[int] = []
    pooled_support: list[int] = []
    radii: list[int] = []
    costs: list[float] = []
    for class_id in range(n_classes):
        radius, cost = select_largest_admissible_radius(probabilities, class_id, lipschitz_constant, eta, weighted=weighted)
        members = list(ordinal_neighborhood(class_id, radius, n_classes))
        pooled = score_values[np.isin(label_values, members)]
        rank = ceil((len(pooled) + 1) * (1.0 - alpha))
        thresholds.append(inf if rank > len(pooled) else float(np.sort(pooled)[rank - 1]))
        ranks.append(None if rank > len(pooled) else rank)
        own_support.append(int(np.count_nonzero(label_values == class_id)))
        pooled_support.append(len(pooled)); radii.append(radius); costs.append(cost)
    return ApproximateCalibrationResult(tuple(thresholds), tuple(ranks), tuple(own_support), tuple(pooled_support), tuple(radii), tuple(costs))
