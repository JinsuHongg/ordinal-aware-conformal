"""Known-distribution generator for adaptive ordinal borrowing v0.3."""
from __future__ import annotations

from dataclasses import dataclass
from math import erf, sqrt
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class Scenario:
    name: str
    means: tuple[float, ...]
    sigma: float


SCENARIOS = {
    "strong_smoothness": Scenario("strong_smoothness", (0.50, 0.505, 0.510, 0.515, 0.520), 0.20),
    "moderate_smoothness": Scenario("moderate_smoothness", (0.50, 0.535, 0.570, 0.605, 0.640), 0.20),
    "local_discontinuity": Scenario("local_discontinuity", (0.50, 0.505, 0.510, 0.80, 0.805), 0.20),
    "no_ordinal_structure": Scenario("no_ordinal_structure", (0.50, 1.10, 0.46, 1.20, 0.40), 0.20),
}


def draw_population(rng: np.random.Generator, size: int, probabilities: Sequence[float], scenario: Scenario) -> tuple[np.ndarray, np.ndarray]:
    labels = rng.choice(len(probabilities), size=size, p=np.asarray(probabilities))
    scores = rng.normal(np.asarray(scenario.means)[labels], scenario.sigma)
    return labels.astype(int), scores


def normal_ks(mean_first: float, mean_second: float, sigma: float) -> float:
    """Exact KS distance for equal-variance normal location families."""
    return erf(abs(mean_first - mean_second) / (2.0 * sqrt(2.0) * sigma))


def true_ks_matrix(scenario: Scenario) -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(normal_ks(first, second, scenario.sigma) for second in scenario.means) for first in scenario.means)
