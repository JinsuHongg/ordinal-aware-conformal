"""Direct non-null two-sample KS structural certificates.

This exploratory module implements Proposition 2b of Underwood and
Paillusson (2024, arXiv:2409.18087).  It is intentionally separate from the
v0.3 DKW certificate: the borrowing and pooled-calibration rules are shared,
but the structural confidence construction is not yet a method change.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import comb, erf, exp, inf, log, sqrt
from typing import Sequence

import numpy as np

from .adaptive_ordinal_borrowing import _ks_distance


@dataclass(frozen=True)
class TwoSampleStructuralCertificates:
    """Pairwise Bonferroni certificates computed from structural data only."""

    counts: tuple[int, ...]
    proportions: tuple[float, ...]
    empirical_ks: tuple[tuple[float, ...], ...]
    pairwise_radii: tuple[tuple[float, ...], ...]
    direct: tuple[tuple[float, ...], ...]
    path: tuple[tuple[float, ...], ...]
    delta: tuple[tuple[float, ...], ...]


def _proposition_2b_term(n: int, m: int, z: float) -> float:
    """The displayed non-swapped term in Proposition 2b, equation (11)."""
    total = n + m
    first = (1.0 + n / total) * 2.0 ** (-m / n)
    first *= exp(-2.0 * m * z * (z - sqrt(log(4.0) / n)))
    argument = sqrt(2.0 * m * m * z * z / total) - sqrt(total * log(2.0) / n)
    second = sqrt(8.0 * np.pi) * z * m * n / total ** 1.5
    second *= exp(-2.0 * m * n * z * z / total) * erf(argument)
    return first + second


def two_sample_ks_tail_bound(n: int, m: int, z: float) -> float:
    """Upper bound for ``P(|d(F_n,G_m)-d(F,G)| > z)``.

    This is Proposition 2b (equation 11) of Underwood and Paillusson.  It is
    applicable to distinct distributions.  The caller must use a radius no
    smaller than :func:`two_sample_ks_minimum_radius`.
    """
    if n <= 0 or m <= 0 or z < two_sample_ks_minimum_radius(n, m):
        return 1.0
    return min(1.0, max(0.0, _proposition_2b_term(n, m, z) + _proposition_2b_term(m, n, z)))


def two_sample_ks_minimum_radius(n: int, m: int) -> float:
    """Domain lower bound in Proposition 2b, including its stated caveat."""
    if n <= 0 or m <= 0:
        return inf
    dkw_domain = sqrt(log(2.0) / 2.0) * (n ** -0.5 + m ** -0.5)
    # The paper notes this extra one-sided-DKWM condition.  Enforcing it makes
    # the numerical inversion conservative rather than silently omitting it.
    one_sided_domain = max(1.0841 * n ** (-2.0 / 3.0), 1.0841 * m ** (-2.0 / 3.0))
    return max(dkw_domain, one_sided_domain)


def two_sample_ks_radius(n: int, m: int, failure_probability: float) -> float:
    """Numerically invert Proposition 2b to a valid distribution-free radius."""
    if n <= 0 or m <= 0:
        return 1.0
    if not 0.0 < failure_probability < 1.0:
        raise ValueError("failure_probability must lie strictly between zero and one")
    lower = two_sample_ks_minimum_radius(n, m)
    if lower >= 1.0 or two_sample_ks_tail_bound(n, m, 1.0) > failure_probability:
        return 1.0
    upper = 1.0
    # Proposition 2b is a tail bound.  Bisection returns the smallest radius
    # within numerical tolerance whose displayed bound is at most delta.
    for _ in range(80):
        middle = (lower + upper) / 2.0
        if two_sample_ks_tail_bound(n, m, middle) <= failure_probability:
            upper = middle
        else:
            lower = middle
    return upper


def two_sample_structural_certificates(
    labels: Sequence[int], scores: Sequence[float], n_classes: int, delta_str: float
) -> TwoSampleStructuralCertificates:
    """Build simultaneous direct/path certificates with pairwise Bonferroni."""
    if not 0.0 < delta_str < 1.0:
        raise ValueError("delta_str must lie strictly between zero and one")
    labels_array, scores_array = np.asarray(labels), np.asarray(scores, dtype=float)
    groups = [np.sort(scores_array[labels_array == class_id]) for class_id in range(n_classes)]
    counts = tuple(len(group) for group in groups)
    total = len(labels_array)
    pair_delta = delta_str / comb(n_classes, 2)
    empirical = np.zeros((n_classes, n_classes))
    radii = np.zeros((n_classes, n_classes))
    direct = np.zeros((n_classes, n_classes))
    for first in range(n_classes):
        for second in range(first + 1, n_classes):
            if counts[first] == 0 or counts[second] == 0:
                empirical[first, second] = empirical[second, first] = 1.0
                radii[first, second] = radii[second, first] = 1.0
                direct[first, second] = direct[second, first] = 1.0
            else:
                empirical_value = _ks_distance(groups[first], groups[second])
                radius = two_sample_ks_radius(counts[first], counts[second], pair_delta)
                empirical[first, second] = empirical[second, first] = empirical_value
                radii[first, second] = radii[second, first] = radius
                direct[first, second] = direct[second, first] = min(1.0, empirical_value + radius)
    path = np.zeros((n_classes, n_classes))
    for first in range(n_classes):
        for second in range(n_classes):
            if first != second:
                path[first, second] = min(1.0, sum(direct[index, index + 1] for index in range(min(first, second), max(first, second))))
    final = np.minimum(direct, path)
    np.fill_diagonal(final, 0.0)
    return TwoSampleStructuralCertificates(
        counts=counts,
        proportions=tuple(count / total for count in counts),
        empirical_ks=tuple(tuple(row) for row in empirical),
        pairwise_radii=tuple(tuple(row) for row in radii),
        direct=tuple(tuple(row) for row in direct),
        path=tuple(tuple(row) for row in path),
        delta=tuple(tuple(row) for row in final),
    )
