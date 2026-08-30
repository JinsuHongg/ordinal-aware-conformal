"""Exploratory guarded local structural-certificate primitives.

The band is Reeve (2024), Corollary 3.  It is uniform in score, which permits
structural-data-measurable interval endpoints.  This module is deliberately
separate from the v0.3 calibration rule.
"""
from __future__ import annotations

from math import ceil, log, sqrt
from typing import Sequence

import numpy as np


def reeve_uniform_upper_radius(empirical_probability: float, sample_size: int, failure_probability: float, beta: float = 2.0) -> float:
    """Data-evaluable one-sided uniform radius from Reeve (2024), Cor. 3."""
    if sample_size <= 0:
        return 1.0
    if not 0.0 < failure_probability < 1.0 or beta <= 1.0:
        raise ValueError("failure_probability must be in (0, 1) and beta must exceed one")
    q = min(1.0, max(0.0, empirical_probability))
    epsilon = log(2.0 * max(1, ceil(log(sample_size, beta))) / failure_probability) / sample_size
    sigma_squared = q * (1.0 - q)
    multiplier = 3.0 * beta - 1.0
    numerator = 3.0 * beta * (2.0 * q - 1.0) * multiplier * epsilon
    numerator += sqrt(epsilon * (18.0 * sigma_squared + epsilon * multiplier * multiplier))
    return min(1.0, max(1.0 / sample_size, numerator / (9.0 + 2.0 * epsilon * multiplier * multiplier)))


def upper_tail_interval(structural_scores: Sequence[float], probability_floor: float) -> tuple[float, float]:
    """A structural-data-measurable interval ``[empirical q_p, infinity)``."""
    if not structural_scores or not 0.0 < probability_floor < 1.0:
        raise ValueError("nonempty scores and probability_floor in (0, 1) are required")
    ordered = np.sort(np.asarray(structural_scores, dtype=float))
    return float(ordered[ceil(probability_floor * len(ordered)) - 1]), float("inf")


def directional_local_ucb(
    source_scores: Sequence[float], target_scores: Sequence[float], interval: tuple[float, float],
    per_direction_failure: float, beta: float = 2.0,
) -> tuple[float, float]:
    """Uniform-in-interval UCB for ``sup_I(F_source-F_target)``.

    The source lower deviation is obtained by reflection.  The added ``1/n``
    covers the empirical-CDF left/right-limit convention at structural jumps.
    """
    source, target = np.sort(np.asarray(source_scores, dtype=float)), np.sort(np.asarray(target_scores, dtype=float))
    if not len(source) or not len(target):
        return 1.0, 1.0
    lower, upper = interval
    grid = np.unique(np.concatenate((source[(source >= lower) & (source <= upper)], target[(target >= lower) & (target <= upper)], np.asarray([lower]))))
    if not len(grid):
        return 0.0, 0.0
    empirical_max, ucb_max = 0.0, 0.0
    for value in grid:
        source_cdf = np.searchsorted(source, value, side="right") / len(source)
        target_cdf = np.searchsorted(target, value, side="right") / len(target)
        source_lower_radius = reeve_uniform_upper_radius(1.0 - source_cdf, len(source), per_direction_failure, beta) + 1.0 / len(source)
        target_upper_radius = reeve_uniform_upper_radius(target_cdf, len(target), per_direction_failure, beta)
        empirical_max = max(empirical_max, source_cdf - target_cdf)
        ucb_max = max(ucb_max, source_cdf - target_cdf + source_lower_radius + target_upper_radius)
    return min(1.0, max(0.0, empirical_max)), min(1.0, max(0.0, ucb_max))
