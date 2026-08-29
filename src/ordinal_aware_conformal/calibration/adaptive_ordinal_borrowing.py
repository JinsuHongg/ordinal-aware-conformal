"""Candidate v0.3 adaptive ordinal-borrowing calibration primitives.

This module implements the executable rule in ``proposed_theory.md``.  It is
an exploratory candidate, not the repository's canonical proposed method.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import ceil, inf, log, sqrt
from typing import Iterable, Sequence

import numpy as np


@dataclass(frozen=True)
class StructuralCertificates:
    counts: tuple[int, ...]
    proportions: tuple[float, ...]
    dkw_radii: tuple[float, ...]
    empirical_ks: tuple[tuple[float, ...], ...]
    direct: tuple[tuple[float, ...], ...]
    path: tuple[tuple[float, ...], ...]
    delta: tuple[tuple[float, ...], ...]


@dataclass(frozen=True)
class NeighborhoodSelection:
    radii: tuple[int, ...]
    epsilons: tuple[float, ...]
    planned_support: tuple[float, ...]
    objectives: tuple[float, ...]


@dataclass(frozen=True)
class CalibrationResult:
    thresholds: tuple[float, ...]
    ranks: tuple[int | None, ...]
    own_support: tuple[int, ...]
    pooled_support: tuple[int, ...]


def ordinal_neighborhood(class_id: int, radius: int, n_classes: int) -> range:
    return range(max(0, class_id - radius), min(n_classes, class_id + radius + 1))


def _ks_distance(first: np.ndarray, second: np.ndarray) -> float:
    """Two-sample empirical KS distance, without a scipy dependency."""
    if not len(first) or not len(second):
        return 1.0
    # Inputs are sorted by ``structural_certificates``.  Evaluating each EDF at
    # the other sample's jumps is equivalent to sorting their concatenation,
    # while avoiding repeated concatenation/sorting for every pair.
    at_first = np.abs(np.arange(1, len(first) + 1) / len(first)
                      - np.searchsorted(second, first, side="right") / len(second))
    at_second = np.abs(np.searchsorted(first, second, side="right") / len(first)
                       - np.arange(1, len(second) + 1) / len(second))
    return float(max(np.max(at_first), np.max(at_second)))


def structural_certificates(labels: Sequence[int], scores: Sequence[float], n_classes: int, delta_str: float) -> StructuralCertificates:
    labels_array, scores_array = np.asarray(labels), np.asarray(scores, dtype=float)
    groups = [np.sort(scores_array[labels_array == class_id]) for class_id in range(n_classes)]
    counts = tuple(len(group) for group in groups)
    total = len(labels_array)
    radii = tuple(1.0 if count == 0 else min(1.0, sqrt(log(2 * n_classes / delta_str) / (2 * count))) for count in counts)
    empirical = np.zeros((n_classes, n_classes))
    direct = np.zeros((n_classes, n_classes))
    for first in range(n_classes):
        for second in range(n_classes):
            if first == second:
                continue
            if counts[first] == 0 or counts[second] == 0:
                empirical[first, second], direct[first, second] = 1.0, 1.0
            else:
                empirical[first, second] = _ks_distance(groups[first], groups[second])
                direct[first, second] = min(1.0, empirical[first, second] + radii[first] + radii[second])
    path = np.zeros((n_classes, n_classes))
    for first in range(n_classes):
        for second in range(n_classes):
            if first != second:
                path[first, second] = min(1.0, sum(direct[index, index + 1] for index in range(min(first, second), max(first, second))))
    final = np.minimum(direct, path)
    np.fill_diagonal(final, 0.0)
    return StructuralCertificates(counts, tuple(count / total for count in counts), radii,
                                  tuple(tuple(row) for row in empirical), tuple(tuple(row) for row in direct),
                                  tuple(tuple(row) for row in path), tuple(tuple(row) for row in final))


def select_neighborhoods(certificates: StructuralCertificates, n_cal: int, alpha: float, radii: Iterable[int] = (0, 1, 2)) -> NeighborhoodSelection:
    n_classes, candidates = len(certificates.counts), tuple(sorted(set(radii)))
    selected_radius, selected_epsilon, selected_support, selected_objective = [], [], [], []
    for class_id in range(n_classes):
        options = []
        for radius in candidates:
            neighborhood = ordinal_neighborhood(class_id, radius, n_classes)
            epsilon = max(certificates.delta[class_id][member] for member in neighborhood)
            planned = n_cal * sum(certificates.proportions[member] for member in neighborhood)
            if epsilon < alpha:
                options.append((epsilon + 1.0 / (planned + 1.0), radius, epsilon, planned))
        # h=0 is always admissible because its epsilon is exactly zero.
        objective, radius, epsilon, planned = min(options, key=lambda item: (item[0], item[1]))
        selected_radius.append(radius); selected_epsilon.append(epsilon)
        selected_support.append(planned); selected_objective.append(objective)
    return NeighborhoodSelection(tuple(selected_radius), tuple(selected_epsilon), tuple(selected_support), tuple(selected_objective))


def _group_scores(labels: Sequence[int], scores: Sequence[float], n_classes: int) -> list[list[float]]:
    grouped = [[] for _ in range(n_classes)]
    for label, score in zip(labels, scores, strict=True):
        grouped[int(label)].append(float(score))
    return grouped


def _quantile(values: list[float], rank: int) -> float:
    return inf if rank > len(values) else sorted(values)[rank - 1]


def fit_independent_mondrian(labels: Sequence[int], scores: Sequence[float], alpha: float, n_classes: int) -> CalibrationResult:
    grouped, thresholds, ranks = _group_scores(labels, scores, n_classes), [], []
    for values in grouped:
        rank = ceil((len(values) + 1) * (1.0 - alpha))
        thresholds.append(_quantile(values, rank)); ranks.append(None if rank > len(values) else rank)
    support = tuple(len(values) for values in grouped)
    return CalibrationResult(tuple(thresholds), tuple(ranks), support, support)


def fit_fixed_ordinal_pooling(labels: Sequence[int], scores: Sequence[float], alpha: float, n_classes: int, radius: int = 1) -> CalibrationResult:
    grouped, thresholds, ranks, pooled = _group_scores(labels, scores, n_classes), [], [], []
    for class_id in range(n_classes):
        values = [score for member in ordinal_neighborhood(class_id, radius, n_classes) for score in grouped[member]]
        rank = ceil((len(values) + 1) * (1.0 - alpha))
        thresholds.append(_quantile(values, rank)); ranks.append(None if rank > len(values) else rank); pooled.append(len(values))
    return CalibrationResult(tuple(thresholds), tuple(ranks), tuple(len(values) for values in grouped), tuple(pooled))


def fit_adaptive_ordinal_borrowing(labels: Sequence[int], scores: Sequence[float], alpha: float, n_classes: int, selection: NeighborhoodSelection, certified: bool) -> CalibrationResult:
    grouped, thresholds, ranks, pooled = _group_scores(labels, scores, n_classes), [], [], []
    for class_id in range(n_classes):
        values = [score for member in ordinal_neighborhood(class_id, selection.radii[class_id], n_classes) for score in grouped[member]]
        epsilon = selection.epsilons[class_id] if certified else 0.0
        rank = ceil((len(values) + 1) * (1.0 - alpha + epsilon))
        invalid = certified and epsilon >= alpha
        thresholds.append(inf if invalid else _quantile(values, rank))
        ranks.append(None if invalid or rank > len(values) else rank); pooled.append(len(values))
    return CalibrationResult(tuple(thresholds), tuple(ranks), tuple(len(values) for values in grouped), tuple(pooled))
