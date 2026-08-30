#!/usr/bin/env python3
"""Oracle novelty stress test: contiguous clusters, paths, and generic donors."""
from __future__ import annotations

import argparse
import csv
import json
from functools import lru_cache
from math import isinf
from pathlib import Path
from statistics import mean

import numpy as np
from scipy.special import ndtr
from scipy.stats import spearmanr

from ordinal_aware_conformal.calibration.adaptive_ordinal_borrowing import fit_independent_mondrian
from ordinal_aware_conformal.calibration.approximate_ordinal_borrowing import ordinal_neighborhood, population_mixture_weights
from ordinal_aware_conformal.calibration.generic_directional_borrowing import (
    direct_directional_cost, fit_generic_directional_borrowing, is_contiguous, is_ordinal_ball, select_generic_group,
)
from ordinal_aware_conformal.calibration.local_path_approximate_borrowing import (
    fit_local_path_approximate_borrowing, path_borrowing_cost, select_support_maximizing_radius,
)
from ordinal_aware_conformal.synthetic.ordinal_borrowing_generator import SCENARIOS, Scenario, draw_population, normal_ks


NAMES = ("strong_smoothness", "moderate_smoothness", "local_discontinuity", "no_ordinal_structure", "nonordinal_favorable_donor")
SLACKS = (0.00, 0.005, 0.01, 0.02, 0.05)
SIZES = (200, 400, 800, 1600)
PROBABILITIES = (0.30, 0.25, 0.22, 0.20, 0.03)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def label(group: tuple[int, ...]) -> str:
    return "|".join(str(index) for index in group)


def normal_cdf(value: float, location: float, sigma: float) -> float:
    return 1.0 if isinf(value) else float(ndtr((value - location) / sigma))


def directional(source: float, target: float, sigma: float) -> float:
    return normal_ks(source, target, sigma) if source < target else 0.0


def directional_matrix(scenario: Scenario) -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(directional(source, target, scenario.sigma) for target in scenario.means) for source in scenario.means)


def edge_costs(scenario: Scenario) -> tuple[tuple[float, ...], tuple[float, ...]]:
    return (tuple(directional(scenario.means[index], scenario.means[index + 1], scenario.sigma) for index in range(4)),
            tuple(directional(scenario.means[index + 1], scenario.means[index], scenario.sigma) for index in range(4)))


def ding_penalty(scenario: Scenario, group: tuple[int, ...]) -> float:
    """Faithful cluster-wide symmetric pairwise-KS analog of Ding Proposition 2."""
    return max(normal_ks(scenario.means[first], scenario.means[second], scenario.sigma) for first in group for second in group)


def select_ding_ball(scenario: Scenario, target: int, eta: float) -> tuple[tuple[int, ...], float]:
    candidates = []
    for radius in range(max(target, 4 - target) + 1):
        group = tuple(ordinal_neighborhood(target, radius, 5))
        penalty = ding_penalty(scenario, group)
        if penalty <= eta + 1e-12:
            candidates.append((sum(PROBABILITIES[index] for index in group), -radius, group, penalty))
    _, _, group, penalty = max(candidates)
    return group, penalty


@lru_cache(maxsize=None)
def oracle_mixture_cost(scenario: Scenario, target: int, group: tuple[int, ...]) -> float:
    weights = {index: PROBABILITIES[index] / sum(PROBABILITIES[value] for value in group) for index in group}
    grid = np.linspace(min(scenario.means) - 8 * scenario.sigma, max(scenario.means) + 8 * scenario.sigma, 20_001)
    mixture = sum(weight * ndtr((grid - scenario.means[index]) / scenario.sigma) for index, weight in weights.items())
    target_cdf = ndtr((grid - scenario.means[target]) / scenario.sigma)
    return max(0.0, float(np.max(mixture - target_cdf)))


def summarize(rows: list[dict[str, object]], keys: tuple[str, ...]) -> list[dict[str, object]]:
    grouped: dict[tuple[object, ...], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(tuple(row[key] for key in keys), []).append(row)
    output = []
    for group, values in sorted(grouped.items()):
        record = dict(zip(keys, group, strict=True))
        record.update({"repetitions": len(values), "selected_group": values[0]["group"], "support_mass": values[0]["support_mass"],
                       "mean_own_support": mean(float(v["own_support"]) for v in values), "mean_pooled_support": mean(float(v["pooled_support"]) for v in values),
                       "mean_cost": mean(float(v["cost"]) for v in values), "guarantee_floor": mean(float(v["guarantee_floor"]) for v in values),
                       "mean_actual_coverage": mean(float(v["actual_coverage"]) for v in values), "finite_rate": mean(int(v["finite"]) for v in values)})
        output.append(record)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/local_path_novelty_stress_test"))
    parser.add_argument("--repetitions", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260828)
    args = parser.parse_args()
    alpha = .10
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "config.json").write_text(json.dumps({"alpha": alpha, "probabilities": PROBABILITIES, "scenarios": NAMES, "slacks": SLACKS, "calibration_sizes": SIZES, "repetitions": args.repetitions, "seed": args.seed, "final_calibration": "ordinary iid population sampling", "oracle_information": True, "ding_penalty": "maximum pairwise symmetric KS within target's contiguous ball"}, indent=2) + "\n")

    support_rows, selected_rows, tightness_rows, alignment_rows = [], [], [], []
    for name in NAMES:
        scenario, matrix = SCENARIOS[name], directional_matrix(SCENARIOS[name])
        forward, backward = edge_costs(scenario)
        for target in range(5):
            distances, discrepancies = [], []
            for source in range(5):
                if source != target:
                    distances.append(abs(source - target)); discrepancies.append(matrix[source][target])
            correlation = float("nan") if len(set(discrepancies)) < 2 else spearmanr(distances, discrepancies).statistic
            alignment_rows.append({"scenario": name, "target": target, "spearman_distance_directional": correlation})
            for radius in range(max(target, 4 - target) + 1):
                group = tuple(ordinal_neighborhood(target, radius, 5))
                direct = direct_directional_cost(PROBABILITIES, target, group, matrix)
                path = path_borrowing_cost(PROBABILITIES, target, radius, forward, backward)
                ding = ding_penalty(scenario, group)
                oracle = oracle_mixture_cost(scenario, target, group)
                tightness_rows.append({"scenario": name, "target": target, "group": label(group), "radius": radius, "oracle_cost": oracle, "direct_cost": direct, "path_cost": path, "ding_penalty": ding,
                                      "path_over_oracle": None if oracle == 0 else path / oracle, "ding_over_oracle": None if oracle == 0 else ding / oracle})
            for eta in SLACKS:
                ding_group, ding_cost = select_ding_ball(scenario, target, eta)
                radius, path_cost = select_support_maximizing_radius(PROBABILITIES, target, forward, backward, eta)
                path_group = tuple(ordinal_neighborhood(target, radius, 5))
                generic_group, generic_cost = select_generic_group(PROBABILITIES, target, matrix, eta)
                methods = (("ding_contiguous", ding_group, ding_cost), ("local_path", path_group, path_cost), ("generic_directional", generic_group, generic_cost))
                masses = {}
                for method, group, cost in methods:
                    mass = sum(PROBABILITIES[index] for index in group); masses[method] = mass
                    support_rows.append({"scenario": name, "target": target, "eta": eta, "method": method, "group": label(group), "support_mass": mass, "expected_support_n200": 200 * mass, "cost": cost})
                    selected_rows.append({"scenario": name, "target": target, "eta": eta, "method": method, "group": label(group), "contiguous": int(is_contiguous(group)), "ordinal_ball": int(is_ordinal_ball(group, target, 5)), "has_distant_source": int(any(abs(index - target) > 1 for index in group)), "excludes_nearer_includes_farther": int(any(abs(farther - target) > abs(nearer - target) and farther in group and nearer not in group for farther in group for nearer in range(5) if nearer != target))})
                for row in support_rows[-3:]:
                    row["path_minus_ding_support"] = masses["local_path"] - masses["ding_contiguous"]
                    row["generic_minus_path_support"] = masses["generic_directional"] - masses["local_path"]
    write_csv(args.output_dir / "support_under_slack.csv", support_rows)
    write_csv(args.output_dir / "selected_groups.csv", selected_rows)
    write_csv(args.output_dir / "cost_tightness.csv", tightness_rows)
    write_csv(args.output_dir / "ordinal_alignment.csv", alignment_rows)
    generic_selection = [row for row in selected_rows if row["method"] == "generic_directional"]
    contiguity = []
    for name in NAMES:
        for target in range(5):
            for eta in SLACKS:
                rows = [row for row in generic_selection if row["scenario"] == name and row["target"] == target and row["eta"] == eta]
                contiguity.append({"scenario": name, "target": target, "eta": eta, "contiguous_rate": mean(row["contiguous"] for row in rows), "ordinal_ball_rate": mean(row["ordinal_ball"] for row in rows), "distant_source_rate": mean(row["has_distant_source"] for row in rows), "exclude_near_include_far_rate": mean(row["excludes_nearer_includes_farther"] for row in rows)})
    write_csv(args.output_dir / "contiguity_summary.csv", contiguity)

    rows = []
    for scenario_number, name in enumerate(NAMES):
        scenario, matrix = SCENARIOS[name], directional_matrix(SCENARIOS[name])
        forward, backward = edge_costs(scenario)
        for n_cal in SIZES:
            for repetition in range(args.repetitions):
                rng = np.random.default_rng(args.seed + scenario_number * 100_000_000 + n_cal * 10_000 + repetition)
                labels, scores = draw_population(rng, n_cal, PROBABILITIES, scenario)
                mondrian = fit_independent_mondrian(labels, scores, alpha, 5)
                for target in range(5):
                    threshold = mondrian.thresholds[target]
                    rows.append({"scenario": name, "n_cal": n_cal, "repetition": repetition, "method": "independent_mondrian", "eta": None, "target": target, "group": str(target), "support_mass": PROBABILITIES[target], "cost": 0.0, "own_support": mondrian.own_support[target], "pooled_support": mondrian.pooled_support[target], "threshold": None if isinf(threshold) else threshold, "finite": int(not isinf(threshold)), "guarantee_floor": .90, "actual_coverage": normal_cdf(threshold, scenario.means[target], scenario.sigma)})
                for eta in SLACKS:
                    local = fit_local_path_approximate_borrowing(labels, scores, alpha, 5, PROBABILITIES, forward, backward, eta)
                    generic = fit_generic_directional_borrowing(labels, scores, alpha, 5, PROBABILITIES, matrix, eta)
                    for target in range(5):
                        ding_group, ding_cost = select_ding_ball(scenario, target, eta)
                        ding_scores = scores[np.isin(labels, ding_group)]
                        rank = int(np.ceil((len(ding_scores) + 1) * .90))
                        ding_threshold = float(np.sort(ding_scores)[rank - 1]) if rank <= len(ding_scores) else float("inf")
                        method_items = (("ding_contiguous", ding_group, ding_cost, ding_threshold, len(ding_scores)), ("local_path", tuple(ordinal_neighborhood(target, local.radii[target], 5)), local.costs[target], local.thresholds[target], local.pooled_support[target]), ("generic_directional", generic.groups[target], generic.costs[target], generic.thresholds[target], generic.pooled_support[target]))
                        for method, group, cost, threshold, pooled in method_items:
                            rows.append({"scenario": name, "n_cal": n_cal, "repetition": repetition, "method": method, "eta": eta, "target": target, "group": label(group), "support_mass": sum(PROBABILITIES[index] for index in group), "cost": cost, "own_support": int(np.count_nonzero(labels == target)), "pooled_support": pooled, "threshold": None if isinf(threshold) else threshold, "finite": int(not isinf(threshold)), "guarantee_floor": .90 - cost, "actual_coverage": normal_cdf(threshold, scenario.means[target], scenario.sigma)})
    write_csv(args.output_dir / "per_repetition.csv", rows)
    write_csv(args.output_dir / "summary.csv", summarize(rows, ("scenario", "n_cal", "method", "eta", "target")))
    rare = [row for row in rows if row["target"] == 4 and row["own_support"] <= 5]
    write_csv(args.output_dir / "rare_support_summary.csv", summarize(rare, ("scenario", "n_cal", "method", "eta", "target")))
    write_csv(args.output_dir / "local_discontinuity_summary.csv", [row for row in summarize(rows, ("scenario", "n_cal", "method", "eta", "target")) if row["scenario"] == "local_discontinuity" and row["target"] == 4])
    write_csv(args.output_dir / "no_structure_summary.csv", [row for row in summarize(rows, ("scenario", "n_cal", "method", "eta", "target")) if row["scenario"] == "no_ordinal_structure" and row["target"] == 4])
    write_csv(args.output_dir / "nonordinal_favorable_donor_summary.csv", [row for row in summarize(rows, ("scenario", "n_cal", "method", "eta", "target")) if row["scenario"] == "nonordinal_favorable_donor" and row["target"] == 4])


if __name__ == "__main__":
    main()
