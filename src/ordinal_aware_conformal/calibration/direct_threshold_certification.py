"""Exact target-class threshold certification for a synthetic feasibility study.

The routines implement a one-sided Clopper--Pearson/tolerance certificate for
a *fixed*, independently proposed score threshold.  They are exploratory and
are deliberately separate from the project's conformal calibration rules.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import ceil, inf, isinf
from typing import Sequence

import numpy as np
from scipy.special import betaincinv
from scipy.stats import binom


@dataclass(frozen=True)
class ThresholdCertification:
    """Result of certifying one fixed score threshold."""

    candidate: float
    threshold: float
    successes: int
    support: int
    lower_bound: float
    accepted: bool


def binomial_survival(successes: int, trials: int, probability: float) -> float:
    """Return the exact binomial survival probability via SciPy."""
    return float(binom.sf(successes - 1, trials, probability))


def clopper_pearson_lower(successes: int, trials: int, delta: float) -> float:
    """Exact one-sided Clopper--Pearson lower bound.

    For ``successes > 0`` this is ``Beta^{-1}(delta; successes,
    trials-successes+1)``.  The scientific stack is already available through
    the project's scikit-learn dependency; ``betaincinv`` evaluates that exact
    beta-quantile representation.
    """
    if not 0.0 < delta < 1.0:
        raise ValueError("delta must lie strictly between zero and one")
    if not 0 <= successes <= trials:
        raise ValueError("successes must be between zero and trials")
    if successes == 0:
        return 0.0
    return float(betaincinv(successes, trials - successes + 1, delta))


@lru_cache(maxsize=None)
def minimum_successes_for_certification(trials: int, target_coverage: float, delta: float) -> int | None:
    """Smallest success count whose exact lower bound reaches the target."""
    if trials < 0:
        raise ValueError("trials must be nonnegative")
    for successes in range(trials + 1):
        if binomial_survival(successes, trials, target_coverage) <= delta:
            return successes
    return None


def exact_acceptance_probability(trials: int, true_coverage: float, target_coverage: float, delta: float) -> float:
    """Acceptance probability for a fixed threshold with known coverage."""
    required = minimum_successes_for_certification(trials, target_coverage, delta)
    return 0.0 if required is None else binomial_survival(required, trials, true_coverage)


def proposal_quantile(scores: Sequence[float], tau: float) -> float:
    """Exact finite-rank pooled proposal threshold; return infinity if invalid."""
    if not 0.0 < tau < 1.0:
        raise ValueError("tau must lie strictly between zero and one")
    rank = ceil((len(scores) + 1) * tau)
    if rank > len(scores):
        return inf
    return float(np.sort(np.asarray(scores, dtype=float))[rank - 1])


def certify_fixed_threshold(candidate: float, certification_scores: Sequence[float], target_coverage: float, delta: float) -> ThresholdCertification:
    """Certify an independent candidate using target-class Bernoulli trials."""
    values = np.asarray(certification_scores, dtype=float)
    if isinf(candidate) or len(values) == 0:
        return ThresholdCertification(float(candidate), inf, 0, len(values), 0.0, False)
    successes = int(np.count_nonzero(values <= candidate))
    lower = clopper_pearson_lower(successes, len(values), delta)
    accepted = lower >= target_coverage
    return ThresholdCertification(float(candidate), float(candidate) if accepted else inf, successes, len(values), lower, accepted)


def direct_pac_threshold(target_scores: Sequence[float], target_coverage: float, delta: float) -> ThresholdCertification:
    """One-sided nonparametric tolerance/PAC threshold using target scores only."""
    values = np.sort(np.asarray(target_scores, dtype=float))
    required = minimum_successes_for_certification(len(values), target_coverage, delta)
    if required is None or required == 0:
        return ThresholdCertification(inf, inf, 0, len(values), 0.0, False)
    candidate = float(values[required - 1])
    lower = clopper_pearson_lower(required, len(values), delta)
    return ThresholdCertification(candidate, candidate, required, len(values), lower, True)
