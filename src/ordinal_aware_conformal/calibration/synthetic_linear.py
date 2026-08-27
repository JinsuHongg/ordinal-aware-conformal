"""Exact-rank calibration rules for the exploratory linear-threshold study.

These rules are deliberately scoped to the synthetic proof-of-concept.  They
are not a canonical proposed method.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import ceil, inf
from typing import Iterable


@dataclass(frozen=True)
class CalibrationResult:
    """Thresholds and diagnostics returned by one calibration rule."""

    thresholds: tuple[float, ...]
    preliminary_thresholds: tuple[float, ...] | None = None
    corrections: tuple[float, ...] | None = None
    final_support: tuple[int, ...] | None = None


def conformal_quantile(scores: Iterable[float], alpha: float) -> float:
    """Return the conservative split-conformal order statistic.

    The rank is ``ceil((n + 1) * (1 - alpha))``.  A rank beyond the available
    sample is represented by ``+inf`` rather than by interpolation or clipping.
    """
    values = sorted(scores)
    rank = ceil((len(values) + 1) * (1.0 - alpha))
    return inf if rank > len(values) else values[rank - 1]


def _scores_by_class(labels: Iterable[int], scores: Iterable[float], n_classes: int) -> list[list[float]]:
    grouped = [[] for _ in range(n_classes)]
    for label, score in zip(labels, scores, strict=True):
        grouped[label].append(score)
    return grouped


def fit_independent_mondrian(
    labels: Iterable[int], scores: Iterable[float], alpha: float, n_classes: int
) -> CalibrationResult:
    """Fit independent true-label Mondrian thresholds."""
    grouped = _scores_by_class(labels, scores, n_classes)
    return CalibrationResult(tuple(conformal_quantile(group, alpha) for group in grouped))


def fit_ordinal_cluster(
    labels: Iterable[int], scores: Iterable[float], alpha: float, n_classes: int, radius: int = 1
) -> CalibrationResult:
    """Fit fixed-neighborhood pooled thresholds (a reference, not class-valid)."""
    grouped = _scores_by_class(labels, scores, n_classes)
    thresholds = []
    for class_id in range(n_classes):
        neighborhood = range(max(0, class_id - radius), min(n_classes, class_id + radius + 1))
        thresholds.append(conformal_quantile((score for member in neighborhood for score in grouped[member]), alpha))
    return CalibrationResult(tuple(thresholds))


def _pinball_loss(residual: float, alpha: float) -> float:
    return (1.0 - alpha) * residual if residual >= 0.0 else -alpha * residual


def _fit_linear_quantile_regression(labels: list[int], scores: list[float], alpha: float, n_classes: int) -> tuple[float, float]:
    """Fit a small deterministic linear quantile regression without new deps.

    For this five-class exploratory problem, minimize pinball loss over a dense
    slope grid and exactly minimize the intercept for each slope with the same
    quantile convention.  This is intentionally transparent and sufficient for
    producing the preliminary diagnostic; final validity never relies on its
    statistical accuracy because it is conformalized on a disjoint split.
    """
    if not scores:
        return 0.0, 0.0
    max_score = max(scores)
    # The score distributions in this generator have nonnegative slopes; retain
    # a small negative range to avoid baking that fact into the fitter.
    bound = max(1.0, 2.0 * max_score / max(1, n_classes - 1))
    steps = 801
    best: tuple[float, float, float] | None = None
    for index in range(steps):
        slope = -bound + 2.0 * bound * index / (steps - 1)
        intercept = conformal_quantile((score - slope * label for label, score in zip(labels, scores)), alpha)
        if intercept == inf:
            # This branch is unreachable for the structured sample sizes used,
            # but preserves a defined fallback for pathological callers.
            continue
        loss = sum(_pinball_loss(score - intercept - slope * label, alpha) for label, score in zip(labels, scores))
        candidate = (loss, abs(slope), slope)
        if best is None or candidate < best:
            best = candidate
            best_intercept = intercept
    if best is None:
        return 0.0, 0.0
    return best_intercept, best[2]


def fit_linear_structured_mondrian(
    structured_labels: Iterable[int],
    structured_scores: Iterable[float],
    final_labels: Iterable[int],
    final_scores: Iterable[float],
    alpha: float,
    n_classes: int,
) -> CalibrationResult:
    """Fit a linear preliminary threshold then exact final Mondrian residuals."""
    struct_labels, struct_scores = list(structured_labels), list(structured_scores)
    beta0, beta1 = _fit_linear_quantile_regression(struct_labels, struct_scores, alpha, n_classes)
    preliminary = tuple(beta0 + beta1 * class_id for class_id in range(n_classes))
    grouped = _scores_by_class(final_labels, final_scores, n_classes)
    corrections = tuple(conformal_quantile((score - preliminary[class_id] for score in group), alpha) for class_id, group in enumerate(grouped))
    thresholds = tuple(preliminary[class_id] + corrections[class_id] for class_id in range(n_classes))
    return CalibrationResult(thresholds, preliminary, corrections, tuple(len(group) for group in grouped))
