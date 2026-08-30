#!/usr/bin/env python3
"""Oracle-edge validation for local-path approximate ordinal borrowing v0.2."""
from __future__ import annotations

import argparse
import csv
import json
from functools import lru_cache
from math import inf, isinf
from pathlib import Path
from statistics import mean

import numpy as np
from scipy.special import ndtr

from ordinal_aware_conformal.calibration.adaptive_ordinal_borrowing import fit_independent_mondrian
from ordinal_aware_conformal.calibration.approximate_ordinal_borrowing import borrowing_cost, fit_approximate_ordinal_borrowing, ordinal_neighborhood, population_mixture_weights
from ordinal_aware_conformal.calibration.local_path_approximate_borrowing import (
    directed_path_cost, fit_local_path_approximate_borrowing, path_borrowing_cost, select_support_maximizing_radius,
)
from ordinal_aware_conformal.synthetic.ordinal_borrowing_generator import SCENARIOS as GENERATOR_SCENARIOS, Scenario, draw_population, normal_ks


SCENARIO_NAMES = ("strong_smoothness", "moderate_smoothness", "local_discontinuity", "no_ordinal_structure")
SLACKS = (0.00, 0.005, 0.01, 0.02, 0.05)
SIZES = (200, 400, 800, 1600)
PROBABILITIES = (0.30, 0.25, 0.22, 0.20, 0.03)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def normal_cdf(value: float, mean_value: float, sigma: float) -> float:
    return 1.0 if isinf(value) else float(ndtr((value - mean_value) / sigma))


def directional_normal(source_mean: float, target_mean: float, sigma: float) -> float:
    return normal_ks(source_mean, target_mean, sigma) if source_mean < target_mean else 0.0


def edges(scenario: Scenario) -> tuple[tuple[float, ...], tuple[float, ...]]:
    forward = tuple(directional_normal(scenario.means[index], scenario.means[index + 1], scenario.sigma) for index in range(len(scenario.means) - 1))
    backward = tuple(directional_normal(scenario.means[index + 1], scenario.means[index], scenario.sigma) for index in range(len(scenario.means) - 1))
    return forward, backward


def global_l(scenario: Scenario) -> float:
    return max(directional_normal(first, second, scenario.sigma) / abs(source - target)
               for source, first in enumerate(scenario.means) for target, second in enumerate(scenario.means) if source != target)


@lru_cache(maxsize=None)
def oracle_cost(scenario: Scenario, class_id: int, radius: int) -> float:
    weights = population_mixture_weights(PROBABILITIES, class_id, radius)
    grid = np.linspace(min(scenario.means) - 8 * scenario.sigma, max(scenario.means) + 8 * scenario.sigma, 20_001)
    mixture = sum(weight * ndtr((grid - location) / scenario.sigma) for location, weight in zip(scenario.means, weights, strict=True))
    target = ndtr((grid - scenario.means[class_id]) / scenario.sigma)
    return max(0.0, float(np.max(mixture - target)))


def ding_cluster_cost(scenario: Scenario, class_id: int, radius: int) -> float:
    return max(normal_ks(scenario.means[source], scenario.means[class_id], scenario.sigma) for source in ordinal_neighborhood(class_id, radius, len(scenario.means)))


def summarize(rows: list[dict[str, object]], keys: tuple[str, ...]) -> list[dict[str, object]]:
    grouped: dict[tuple[object, ...], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(tuple(row[key] for key in keys), []).append(row)
    output = []
    for group, values in sorted(grouped.items()):
        record = dict(zip(keys, group, strict=True))
        record.update({"repetitions": len(values), "mean_own_support": mean(float(v["own_support"]) for v in values),
                       "mean_pooled_support": mean(float(v["pooled_support"]) for v in values),
                       "mean_radius": mean(float(v["radius"]) for v in values), "mean_cost": mean(float(v["cost"]) for v in values),
                       "mean_global_cost": mean(float(v["global_cost"]) for v in values), "mean_oracle_cost": mean(float(v["oracle_cost"]) for v in values),
                       "mean_ding_cluster_cost": mean(float(v["ding_cluster_cost"]) for v in values),
                       "guarantee_floor": mean(float(v["guarantee_floor"]) for v in values),
                       "mean_actual_coverage": mean(float(v["actual_coverage"]) for v in values),
                       "finite_rate": mean(int(v["finite"]) for v in values)})
        output.append(record)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/synthetic_local_path_approximate_borrowing_v0_2"))
    parser.add_argument("--repetitions", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260828)
    args = parser.parse_args()
    alpha, n_classes = .10, 5
    args.output_dir.mkdir(parents=True, exist_ok=True)
    config = {"study": "local_path_approximate_ordinal_borrowing_v0_2", "alpha": alpha, "probabilities": PROBABILITIES,
              "calibration_sizes": SIZES, "slacks": SLACKS, "repetitions": args.repetitions, "seed": args.seed,
              "final_calibration": "ordinary iid population sampling", "edge_costs": "true oracle directed adjacent discrepancies", "selection": "maximize population neighborhood mass subject to path cost <= eta"}
    (args.output_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")

    path_rows, direction_rows, ding_rows = [], [], []
    for name in SCENARIO_NAMES:
        scenario = GENERATOR_SCENARIOS[name]
        forward, backward, maximum = (*edges(scenario), global_l(scenario))
        symmetric = tuple(max(first, second) for first, second in zip(forward, backward, strict=True))
        for class_id in range(n_classes):
            for radius in range(max(class_id, n_classes - class_id - 1) + 1):
                path = path_borrowing_cost(PROBABILITIES, class_id, radius, forward, backward)
                global_cost = borrowing_cost(PROBABILITIES, class_id, radius, maximum)
                oracle = oracle_cost(scenario, class_id, radius)
                ding = ding_cluster_cost(scenario, class_id, radius)
                path_rows.append({"scenario": name, "class_id": class_id, "radius": radius, "global_L": maximum, "path_cost": path,
                                  "global_cost": global_cost, "oracle_cost": oracle, "ding_cluster_cost": ding,
                                  "path_over_oracle": None if oracle == 0 else path / oracle, "global_over_oracle": None if oracle == 0 else global_cost / oracle})
        for eta in SLACKS:
            for class_id in range(n_classes):
                directed_radius, directed_cost = select_support_maximizing_radius(PROBABILITIES, class_id, forward, backward, eta)
                symmetric_radius, symmetric_cost = select_support_maximizing_radius(PROBABILITIES, class_id, symmetric, symmetric, eta)
                direction_rows.append({"scenario": name, "eta": eta, "class_id": class_id, "directed_radius": directed_radius, "directed_cost": directed_cost,
                                       "symmetric_radius": symmetric_radius, "symmetric_cost": symmetric_cost})
        for source, target in ((3, 4), (2, 4), (1, 4)):
            ding_rows.append({"scenario": name, "source": source, "target": target, "directed_path_cost": directed_path_cost(source, target, forward, backward),
                              "lambda_0_plus": forward[0], "lambda_0_minus": backward[0], "lambda_1_plus": forward[1], "lambda_1_minus": backward[1],
                              "lambda_2_plus": forward[2], "lambda_2_minus": backward[2], "lambda_3_plus": forward[3], "lambda_3_minus": backward[3]})
    write_csv(args.output_dir / "path_cost_summary.csv", path_rows)
    write_csv(args.output_dir / "directionality_ablation.csv", direction_rows)
    write_csv(args.output_dir / "ding_comparison.csv", path_rows)
    write_csv(args.output_dir / "local_discontinuity_summary.csv", [row for row in ding_rows if row["scenario"] == "local_discontinuity"])

    rows = []
    for scenario_number, name in enumerate(SCENARIO_NAMES):
        scenario = GENERATOR_SCENARIOS[name]
        forward, backward, maximum = (*edges(scenario), global_l(scenario))
        for n_cal in SIZES:
            for repetition in range(args.repetitions):
                rng = np.random.default_rng(args.seed + scenario_number * 100_000_000 + n_cal * 10_000 + repetition)
                labels, scores = draw_population(rng, n_cal, PROBABILITIES, scenario)
                mondrian = fit_independent_mondrian(labels, scores, alpha, n_classes)
                for class_id in range(n_classes):
                    threshold = mondrian.thresholds[class_id]
                    rows.append({"scenario": name, "n_cal": n_cal, "repetition": repetition, "method": "independent_mondrian", "eta": None, "class_id": class_id,
                                 "radius": 0, "cost": 0.0, "global_cost": 0.0, "oracle_cost": 0.0, "ding_cluster_cost": 0.0,
                                 "own_support": mondrian.own_support[class_id], "pooled_support": mondrian.pooled_support[class_id],
                                 "threshold": None if isinf(threshold) else threshold, "finite": int(not isinf(threshold)), "guarantee_floor": .90,
                                 "actual_coverage": normal_cdf(threshold, scenario.means[class_id], scenario.sigma)})
                for eta in SLACKS:
                    global_rule = fit_approximate_ordinal_borrowing(labels, scores, alpha, n_classes, PROBABILITIES, maximum, eta)
                    local_rule = fit_local_path_approximate_borrowing(labels, scores, alpha, n_classes, PROBABILITIES, forward, backward, eta)
                    for method, result in (("v0_1_global_L", global_rule), ("v0_2_local_path", local_rule)):
                        for class_id in range(n_classes):
                            radius, threshold = result.radii[class_id], result.thresholds[class_id]
                            cost = result.costs[class_id]
                            rows.append({"scenario": name, "n_cal": n_cal, "repetition": repetition, "method": method, "eta": eta, "class_id": class_id,
                                         "radius": radius, "cost": cost, "global_cost": borrowing_cost(PROBABILITIES, class_id, radius, maximum),
                                         "oracle_cost": oracle_cost(scenario, class_id, radius), "ding_cluster_cost": ding_cluster_cost(scenario, class_id, radius),
                                         "own_support": result.own_support[class_id], "pooled_support": result.pooled_support[class_id],
                                         "threshold": None if isinf(threshold) else threshold, "finite": int(not isinf(threshold)),
                                         "guarantee_floor": 1.0 - alpha - cost, "actual_coverage": normal_cdf(threshold, scenario.means[class_id], scenario.sigma)})
    write_csv(args.output_dir / "per_repetition.csv", rows)
    write_csv(args.output_dir / "summary.csv", summarize(rows, ("scenario", "n_cal", "method", "eta", "class_id")))
    rare = [row for row in rows if row["class_id"] == 4 and row["own_support"] <= 5]
    write_csv(args.output_dir / "rare_support_summary.csv", summarize(rare, ("scenario", "n_cal", "method", "eta", "class_id")))


if __name__ == "__main__":
    main()
