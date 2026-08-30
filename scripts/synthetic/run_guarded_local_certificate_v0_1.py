#!/usr/bin/env python3
"""Oracle and finite-sample feasibility study for guarded local certificates."""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from math import ceil, erf, inf, isinf, sqrt
from pathlib import Path
from statistics import mean

import numpy as np

from ordinal_aware_conformal.calibration.adaptive_ordinal_borrowing import structural_certificates
from ordinal_aware_conformal.calibration.guarded_local_certificate import directional_local_ucb, upper_tail_interval
from ordinal_aware_conformal.calibration.two_sample_ks_certificate import two_sample_structural_certificates
from ordinal_aware_conformal.synthetic.ordinal_borrowing_generator import SCENARIOS, draw_population, normal_ks


SIZES = (500, 1_000, 2_000, 5_000, 10_000, 20_000, 50_000)
PROBABILITY_FLOORS = (0.70, 0.80, 0.85, 0.90)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def normal_cdf(value: float, mean_value: float, sigma: float) -> float:
    return 0.5 * (1.0 + erf((value - mean_value) / (sqrt(2.0) * sigma)))


def mixture_quantile(probability: float, means: tuple[float, ...], sigma: float, weights: tuple[float, ...]) -> float:
    lower, upper = min(means) - 8 * sigma, max(means) + 8 * sigma
    for _ in range(100):
        middle = (lower + upper) / 2
        cdf = sum(weight * normal_cdf(middle, mean_value, sigma) for mean_value, weight in zip(means, weights, strict=True))
        if cdf < probability: lower = middle
        else: upper = middle
    return upper


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/synthetic_guarded_local_certificate_v0_1"))
    parser.add_argument("--repetitions", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260828)
    args = parser.parse_args()
    alpha, delta_str, n_classes, n_cal, source, target = 0.10, 0.05, 5, 200, 3, 4
    probabilities, scenario = (0.30, 0.25, 0.22, 0.20, 0.03), SCENARIOS["strong_smoothness"]
    local_pair_delta = delta_str / (2 * n_classes)
    pair_weights = (probabilities[source] / (probabilities[source] + probabilities[target]), probabilities[target] / (probabilities[source] + probabilities[target]))
    global_truth = normal_ks(scenario.means[source], scenario.means[target], scenario.sigma)
    oracle_rows = []
    for floor in PROBABILITY_FLOORS:
        lower = mixture_quantile(floor, (scenario.means[source], scenario.means[target]), scenario.sigma, pair_weights)
        local_truth = normal_cdf(lower, scenario.means[source], scenario.sigma) - normal_cdf(lower, scenario.means[target], scenario.sigma)
        oracle_rows.append({"probability_floor": floor, "population_interval_lower": lower, "true_global_directional_discrepancy": global_truth, "true_local_directional_discrepancy": local_truth})
    args.output_dir.mkdir(parents=True, exist_ok=True)
    config = {"study": "guarded_local_certificate_v0_1_feasibility", "alpha": alpha, "delta_str": delta_str, "n_cal": n_cal, "n_classes": n_classes, "probability_floors": PROBABILITY_FLOORS, "structural_sizes": SIZES, "repetitions": args.repetitions, "seed": args.seed, "scenario": scenario.name, "per_direction_failure": local_pair_delta, "local_bound": "Reeve (2024) Corollary 3, beta=2, both CDF directions"}
    (args.output_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n"); write_csv(args.output_dir / "oracle_local_summary.csv", oracle_rows)
    rows = []
    for n_str in SIZES:
        for repetition in range(args.repetitions):
            structural_rng = np.random.default_rng(args.seed + n_str * 10_000 + repetition)
            calibration_rng = np.random.default_rng(args.seed + 9_000_000 + repetition)
            labels, scores = draw_population(structural_rng, n_str, probabilities, scenario)
            cal_labels, cal_scores = draw_population(calibration_rng, n_cal, probabilities, scenario)
            dkw = structural_certificates(labels, scores, n_classes, delta_str)
            two_sample = two_sample_structural_certificates(labels, scores, n_classes, delta_str)
            source_scores, target_scores = scores[labels == source], scores[labels == target]
            pooled_structural = list(source_scores) + list(target_scores)
            pooled_calibration = np.sort(cal_scores[(cal_labels == source) | (cal_labels == target)])
            for floor, oracle in zip(PROBABILITY_FLOORS, oracle_rows, strict=True):
                interval = upper_tail_interval(pooled_structural, floor)
                empirical, local_ucb = directional_local_ucb(source_scores, target_scores, interval, local_pair_delta)
                rank = ceil((len(pooled_calibration) + 1) * (1 - alpha + local_ucb))
                rank_finite = local_ucb < alpha and rank <= len(pooled_calibration)
                tilde_q = inf if not rank_finite else float(pooled_calibration[rank - 1])
                in_interval = int(not isinf(tilde_q) and tilde_q >= interval[0])
                oracle_epsilon = float(oracle["true_local_directional_discrepancy"])
                oracle_rank = ceil((len(pooled_calibration) + 1) * (1 - alpha + oracle_epsilon))
                oracle_finite = oracle_epsilon < alpha and oracle_rank <= len(pooled_calibration)
                oracle_q = inf if not oracle_finite else float(pooled_calibration[oracle_rank - 1])
                rows.append({"n_str": n_str, "repetition": repetition, "probability_floor": floor, "m3": len(source_scores), "m4": len(target_scores), "interval_lower": interval[0], "empirical_local_directional": empirical, "local_ucb": local_ucb, "dkw_ucb": dkw.delta[source][target], "two_sample_ucb": two_sample.delta[source][target], "oracle_local_discrepancy": oracle_epsilon, "local_admissible": int(local_ucb < alpha), "rank": rank if rank_finite else None, "rank_finite": int(rank_finite), "tilde_q": None if isinf(tilde_q) else tilde_q, "guard_in_region": in_interval, "guard_feasible": int(rank_finite and in_interval), "oracle_rank_finite": int(oracle_finite), "oracle_guard_in_region": int(not isinf(oracle_q) and oracle_q >= float(oracle["population_interval_lower"])), "oracle_guard_feasible": int(oracle_finite and not isinf(oracle_q) and oracle_q >= float(oracle["population_interval_lower"]))})
    write_csv(args.output_dir / "certificate_per_repetition.csv", rows)
    summary = []
    for n_str in SIZES:
        for floor in PROBABILITY_FLOORS:
            values = [row for row in rows if row["n_str"] == n_str and row["probability_floor"] == floor]
            summary.append({"n_str": n_str, "probability_floor": floor, "repetitions": len(values), "mean_m4": mean(float(row["m4"]) for row in values), "mean_empirical_local_directional": mean(float(row["empirical_local_directional"]) for row in values), "mean_local_ucb": mean(float(row["local_ucb"]) for row in values), "mean_dkw_ucb": mean(float(row["dkw_ucb"]) for row in values), "mean_two_sample_ucb": mean(float(row["two_sample_ucb"]) for row in values), "p_local_ucb_below_alpha": mean(int(row["local_admissible"]) for row in values), "p_rank_finite": mean(int(row["rank_finite"]) for row in values), "p_guard_in_region": mean(int(row["guard_in_region"]) for row in values), "p_guard_feasible": mean(int(row["guard_feasible"]) for row in values), "p_oracle_guard_feasible": mean(int(row["oracle_guard_feasible"]) for row in values)})
    write_csv(args.output_dir / "certificate_summary.csv", summary)
    guard_rows = [row for row in summary if row["probability_floor"] in PROBABILITY_FLOORS]
    write_csv(args.output_dir / "guard_summary.csv", guard_rows)


if __name__ == "__main__":
    main()
