#!/usr/bin/env python3
"""Minimal validation of fixed-assumption approximate ordinal borrowing."""
from __future__ import annotations

import argparse
import csv
import json
from math import erf, inf, isinf, sqrt
from pathlib import Path
from statistics import mean

import numpy as np

from ordinal_aware_conformal.calibration.adaptive_ordinal_borrowing import fit_fixed_ordinal_pooling, fit_independent_mondrian
from ordinal_aware_conformal.calibration.approximate_ordinal_borrowing import (
    borrowing_cost, fit_approximate_ordinal_borrowing, ordinal_neighborhood,
    population_mixture_weights, select_largest_admissible_radius, worst_case_borrowing_cost,
)
from ordinal_aware_conformal.synthetic.ordinal_borrowing_generator import SCENARIOS, Scenario, draw_population, normal_ks


SCENARIO_NAMES = ("strong_smoothness", "moderate_smoothness", "local_discontinuity", "no_ordinal_structure")
SLACKS = (0.00, 0.01, 0.02, 0.05)
CALIBRATION_SIZES = (200, 400, 800, 1600)
PROBABILITIES = (0.30, 0.25, 0.22, 0.20, 0.03)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def normal_cdf(value: float, mean_value: float, sigma: float) -> float:
    if isinf(value):
        return 1.0
    return 0.5 * (1.0 + erf((value - mean_value) / (sqrt(2.0) * sigma)))


def directional_normal_discrepancy(source_mean: float, target_mean: float, sigma: float) -> float:
    """sup_t F_source(t)-F_target(t) for equal-variance normal laws."""
    return normal_ks(source_mean, target_mean, sigma) if source_mean < target_mean else 0.0


def minimal_directional_lipschitz_constant(scenario: Scenario) -> float:
    values = []
    for source, source_mean in enumerate(scenario.means):
        for target, target_mean in enumerate(scenario.means):
            if source != target:
                values.append(directional_normal_discrepancy(source_mean, target_mean, scenario.sigma) / abs(source - target))
    return max(values)


def oracle_directional_cost(scenario: Scenario, class_id: int, radius: int) -> float:
    weights = population_mixture_weights(PROBABILITIES, class_id, radius)
    lower, upper = min(scenario.means) - 8 * scenario.sigma, max(scenario.means) + 8 * scenario.sigma
    grid = np.linspace(lower, upper, 20_001)
    mixture = sum(weight * np.vectorize(normal_cdf)(grid, location, scenario.sigma) for location, weight in zip(scenario.means, weights, strict=True))
    target = np.vectorize(normal_cdf)(grid, scenario.means[class_id], scenario.sigma)
    return max(0.0, float(np.max(mixture - target)))


def summarize(rows: list[dict[str, object]], keys: tuple[str, ...]) -> list[dict[str, object]]:
    groups: dict[tuple[object, ...], list[dict[str, object]]] = {}
    for row in rows:
        groups.setdefault(tuple(row[key] for key in keys), []).append(row)
    result = []
    for group_key, values in sorted(groups.items()):
        summary = dict(zip(keys, group_key, strict=True))
        summary.update({
            "repetitions": len(values), "mean_own_support": mean(float(row["own_support"]) for row in values),
            "mean_pooled_support": mean(float(row["pooled_support"]) for row in values),
            "mean_support_multiplier": mean(float(row["support_multiplier"]) for row in values if row["support_multiplier"] is not None),
            "mean_radius": mean(float(row["radius"]) for row in values), "mean_cost": mean(float(row["borrowing_cost"]) for row in values),
            "guarantee_floor": mean(float(row["guarantee_floor"]) for row in values),
            "mean_actual_coverage": mean(float(row["actual_coverage"]) for row in values),
            "finite_rate": mean(int(row["finite"]) for row in values),
            "realized_threshold_above_floor_rate": mean(int(row["actual_coverage"] + 1e-12 >= row["guarantee_floor"]) for row in values),
        })
        result.append(summary)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/synthetic_approximate_ordinal_borrowing_v0_1"))
    parser.add_argument("--repetitions", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260828)
    args = parser.parse_args()
    alpha, n_classes = 0.10, 5
    args.output_dir.mkdir(parents=True, exist_ok=True)
    config = {"study": "approximate_ordinal_class_conditional_v0_1", "alpha": alpha, "probabilities": PROBABILITIES,
              "calibration_sizes": CALIBRATION_SIZES, "slacks": SLACKS, "repetitions": args.repetitions, "seed": args.seed,
              "final_calibration": "ordinary iid population sampling", "lipschitz_constant": "true minimal global directional L in each synthetic scenario", "selection": "largest population-mixture-weighted slack-admissible ordinal radius"}
    (args.output_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    oracle_rows = []
    for scenario_name in SCENARIO_NAMES:
        scenario = SCENARIOS[scenario_name]
        lipschitz = minimal_directional_lipschitz_constant(scenario)
        for class_id in range(n_classes):
            for radius in range(n_classes):
                if radius > max(class_id, n_classes - class_id - 1):
                    continue
                oracle_rows.append({"scenario": scenario_name, "class_id": class_id, "radius": radius, "lipschitz_constant": lipschitz,
                                    "weighted_cost": borrowing_cost(PROBABILITIES, class_id, radius, lipschitz),
                                    "worst_cost": worst_case_borrowing_cost(radius, lipschitz),
                                    "oracle_directional_cost": oracle_directional_cost(scenario, class_id, radius)})
    write_csv(args.output_dir / "oracle_cost_summary.csv", oracle_rows)

    rows = []
    for scenario_number, scenario_name in enumerate(SCENARIO_NAMES):
        scenario = SCENARIOS[scenario_name]
        lipschitz = minimal_directional_lipschitz_constant(scenario)
        for n_cal in CALIBRATION_SIZES:
            for repetition in range(args.repetitions):
                rng = np.random.default_rng(args.seed + scenario_number * 100_000_000 + n_cal * 10_000 + repetition)
                labels, scores = draw_population(rng, n_cal, PROBABILITIES, scenario)
                mondrian = fit_independent_mondrian(labels, scores, alpha, n_classes)
                fixed = fit_fixed_ordinal_pooling(labels, scores, alpha, n_classes, radius=1)
                method_results = [("independent_mondrian", None, mondrian, [0] * n_classes, [0.0] * n_classes)]
                fixed_radii = [min(1, max(class_id, n_classes - class_id - 1)) for class_id in range(n_classes)]
                fixed_costs = [borrowing_cost(PROBABILITIES, class_id, radius, lipschitz) for class_id, radius in enumerate(fixed_radii)]
                method_results.append(("fixed_ordinal_pooling", None, fixed, fixed_radii, fixed_costs))
                for eta in SLACKS:
                    approximate = fit_approximate_ordinal_borrowing(labels, scores, alpha, n_classes, PROBABILITIES, lipschitz, eta)
                    method_results.append(("approximate_ordinal_borrowing", eta, approximate, approximate.radii, approximate.costs))
                for method, eta, result, radii, costs in method_results:
                    for class_id in range(n_classes):
                        own, pooled, threshold = result.own_support[class_id], result.pooled_support[class_id], result.thresholds[class_id]
                        rows.append({"scenario": scenario_name, "n_cal": n_cal, "repetition": repetition, "method": method, "eta": eta,
                                    "class_id": class_id, "lipschitz_constant": lipschitz, "radius": radii[class_id], "borrowing_cost": costs[class_id],
                                    "guarantee_floor": 1.0 - alpha - costs[class_id], "slack_floor": None if eta is None else 1.0 - alpha - eta,
                                    "own_support": own, "pooled_support": pooled, "support_multiplier": pooled / own if own else None,
                                    "threshold": None if isinf(threshold) else threshold, "finite": int(not isinf(threshold)),
                                    "actual_coverage": normal_cdf(threshold, scenario.means[class_id], scenario.sigma)})
    write_csv(args.output_dir / "per_repetition.csv", rows)
    write_csv(args.output_dir / "summary.csv", summarize(rows, ("scenario", "n_cal", "method", "eta", "class_id")))
    rare = [row for row in rows if row["class_id"] == 4 and row["own_support"] <= 5]
    write_csv(args.output_dir / "rare_support_summary.csv", summarize(rare, ("scenario", "n_cal", "method", "eta", "class_id")))
    tradeoff = [row for row in summarize(rows, ("scenario", "n_cal", "method", "eta", "class_id")) if row["method"] == "approximate_ordinal_borrowing" and row["class_id"] == 4]
    write_csv(args.output_dir / "slack_tradeoff_summary.csv", tradeoff)
    weighted_vs_worst = []
    for scenario_name in SCENARIO_NAMES:
        lipschitz = minimal_directional_lipschitz_constant(SCENARIOS[scenario_name])
        for eta in SLACKS:
            for class_id in range(n_classes):
                weighted_radius, weighted_cost = select_largest_admissible_radius(PROBABILITIES, class_id, lipschitz, eta, weighted=True)
                worst_radius, worst_cost = select_largest_admissible_radius(PROBABILITIES, class_id, lipschitz, eta, weighted=False)
                weighted_vs_worst.append({"scenario": scenario_name, "eta": eta, "class_id": class_id, "weighted_radius": weighted_radius,
                                          "weighted_cost": weighted_cost, "worst_radius": worst_radius, "worst_cost": worst_cost})
    write_csv(args.output_dir / "weighted_vs_worst_summary.csv", weighted_vs_worst)


if __name__ == "__main__":
    main()
