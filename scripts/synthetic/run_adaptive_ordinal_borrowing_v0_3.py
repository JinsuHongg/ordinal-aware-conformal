#!/usr/bin/env python3
"""Run the theorem-aligned synthetic validation of adaptive borrowing v0.3.

The scores are direct draws from known true-label distributions, so this run
evaluates threshold inclusion and coverage.  It intentionally does not invent
candidate-class scores, and hence prediction-set sizes are not meaningful.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from collections import defaultdict
from math import isinf
from pathlib import Path
from statistics import mean

import numpy as np

from ordinal_aware_conformal.calibration.adaptive_ordinal_borrowing import (
    fit_adaptive_ordinal_borrowing, fit_fixed_ordinal_pooling,
    fit_independent_mondrian, select_neighborhoods, structural_certificates,
)
from ordinal_aware_conformal.synthetic.ordinal_borrowing_generator import SCENARIOS, draw_population, true_ks_matrix


METHODS = ("independent_mondrian", "fixed_ordinal_pooling_h1", "adaptive_approximate", "adaptive_certified_v0_3")


def git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def _mean(values: list[float]) -> float | None:
    return mean(values) if values else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/synthetic_adaptive_ordinal_borrowing_v0_3"))
    parser.add_argument("--repetitions", type=int, default=100)
    parser.add_argument("--structural-size", type=int, default=50_000)
    parser.add_argument("--test-size", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=20260828)
    args = parser.parse_args()
    n_classes, alpha, delta_str, rare_class = 5, 0.10, 0.05, 4
    probabilities, calibration_sizes = (0.30, 0.25, 0.22, 0.20, 0.03), (200, 400, 800, 1600)
    config: dict[str, object] = {
        "study": "synthetic_adaptive_ordinal_borrowing_v0_3", "method_version": "candidate-v0.3",
        "n_classes": n_classes, "alpha": alpha, "delta_str": delta_str, "rare_class": rare_class,
        "class_probabilities": probabilities, "calibration_sizes": calibration_sizes,
        "structural_size": args.structural_size, "test_size": args.test_size, "repetitions": args.repetitions,
        "seed": args.seed, "score": "direct true-label S | Y=k ~ Normal(mu_k, 0.20^2); no candidate-class scores",
        "final_calibration_sampling": "ordinary i.i.d. population sample; not fixed-count or stratified",
        "candidate_radii": [0, 1, 2], "fixed_pool_radius": 1,
        "scenarios": {name: {"means": scenario.means, "sigma": scenario.sigma} for name, scenario in SCENARIOS.items()},
    }
    config["config_hash"] = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    config["code_commit"] = git_commit()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    rows: list[dict[str, object]] = []
    pair_rows: list[dict[str, object]] = []
    for scenario_index, (scenario_name, scenario) in enumerate(SCENARIOS.items()):
        truth = true_ks_matrix(scenario)
        for n_cal in calibration_sizes:
            for repetition in range(args.repetitions):
                rng = np.random.default_rng(args.seed + scenario_index * 10_000_000 + n_cal * 1_000 + repetition)
                structural_labels, structural_scores = draw_population(rng, args.structural_size, probabilities, scenario)
                calibration_labels, calibration_scores = draw_population(rng, n_cal, probabilities, scenario)
                test_labels, test_scores = draw_population(rng, args.test_size, probabilities, scenario)
                certificates = structural_certificates(structural_labels, structural_scores, n_classes, delta_str)
                selection = select_neighborhoods(certificates, n_cal, alpha)
                results = {
                    "independent_mondrian": fit_independent_mondrian(calibration_labels, calibration_scores, alpha, n_classes),
                    "fixed_ordinal_pooling_h1": fit_fixed_ordinal_pooling(calibration_labels, calibration_scores, alpha, n_classes),
                    "adaptive_approximate": fit_adaptive_ordinal_borrowing(calibration_labels, calibration_scores, alpha, n_classes, selection, certified=False),
                    "adaptive_certified_v0_3": fit_adaptive_ordinal_borrowing(calibration_labels, calibration_scores, alpha, n_classes, selection, certified=True),
                }
                all_pairs_covered = True
                for first in range(n_classes):
                    for second in range(first + 1, n_classes):
                        covered = truth[first][second] <= certificates.delta[first][second]
                        all_pairs_covered &= covered
                        pair_rows.append({"scenario": scenario_name, "n_cal": n_cal, "repetition": repetition, "class_j": first, "class_k": second,
                                          "true_ks": truth[first][second], "empirical_ks": certificates.empirical_ks[first][second],
                                          "direct_certificate": certificates.direct[first][second], "path_certificate": certificates.path[first][second],
                                          "final_certificate": certificates.delta[first][second], "certificate_covers_true_ks": int(covered),
                                          "simultaneous_certificate_covers_all_pairs": int(all_pairs_covered)})
                for method, result in results.items():
                    for class_id in range(n_classes):
                        mask = test_labels == class_id
                        threshold = result.thresholds[class_id]
                        coverage = 1.0 if isinf(threshold) else float(np.mean(test_scores[mask] <= threshold))
                        rows.append({"scenario": scenario_name, "n_cal": n_cal, "repetition": repetition, "method": method, "class_id": class_id,
                                     "test_count": int(mask.sum()), "coverage": coverage, "threshold": None if isinf(threshold) else threshold,
                                     "threshold_is_infinite": int(isinf(threshold)), "rank": result.ranks[class_id],
                                     "own_calibration_count": result.own_support[class_id], "pooled_calibration_count": result.pooled_support[class_id],
                                     "selected_radius": selection.radii[class_id], "certified_epsilon": selection.epsilons[class_id],
                                     "planned_pooled_support": selection.planned_support[class_id], "selection_objective": selection.objectives[class_id],
                                     "structural_count": certificates.counts[class_id], "dkw_radius": certificates.dkw_radii[class_id]})
    write_csv(args.output_dir / "per_repetition.csv", rows)
    write_csv(args.output_dir / "pairwise_certificate_summary.csv", pair_rows)
    grouped: dict[tuple[str, int, str, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows: grouped[(str(row["scenario"]), int(row["n_cal"]), str(row["method"]), int(row["class_id"]))].append(row)
    summary = []
    for key, values in sorted(grouped.items()):
        scenario, n_cal, method, class_id = key
        summary.append({"scenario": scenario, "n_cal": n_cal, "method": method, "class_id": class_id,
                        "repetitions": len(values), "mean_coverage": mean(float(v["coverage"]) for v in values),
                        "finite_threshold_rate": 1 - mean(int(v["threshold_is_infinite"]) for v in values),
                        "infinite_threshold_rate": mean(int(v["threshold_is_infinite"]) for v in values),
                        "mean_selected_radius": mean(int(v["selected_radius"]) for v in values),
                        "mean_certified_epsilon": mean(float(v["certified_epsilon"]) for v in values),
                        "mean_own_calibration_count": mean(int(v["own_calibration_count"]) for v in values),
                        "mean_pooled_calibration_count": mean(int(v["pooled_calibration_count"]) for v in values),
                        "mean_marginal_coverage": None, "mean_worst_class_coverage": None})
    for scenario_name in SCENARIOS:
        for n_cal in calibration_sizes:
            for method in METHODS:
                by_repetition = defaultdict(list)
                for row in rows:
                    if row["scenario"] == scenario_name and row["n_cal"] == n_cal and row["method"] == method:
                        by_repetition[int(row["repetition"])].append(row)
                summary.append({"scenario": scenario_name, "n_cal": n_cal, "method": method, "class_id": "ALL",
                                "repetitions": len(by_repetition), "mean_coverage": None, "finite_threshold_rate": None,
                                "infinite_threshold_rate": None, "mean_selected_radius": None, "mean_certified_epsilon": None,
                                "mean_own_calibration_count": None, "mean_pooled_calibration_count": None,
                                "mean_marginal_coverage": mean(sum(float(v["coverage"]) * int(v["test_count"]) for v in values) / sum(int(v["test_count"]) for v in values) for values in by_repetition.values()),
                                "mean_worst_class_coverage": mean(min(float(v["coverage"]) for v in values) for values in by_repetition.values())})
    write_csv(args.output_dir / "summary.csv", summary)
    rare_rows = [row for row in rows if int(row["class_id"]) == rare_class]
    bins = (("n4_le_5", lambda n: n <= 5), ("n4_6_10", lambda n: 6 <= n <= 10), ("n4_11_20", lambda n: 11 <= n <= 20), ("n4_21_50", lambda n: 21 <= n <= 50), ("n4_gt_50", lambda n: n > 50))
    rare_summary = []
    for scenario_name in SCENARIOS:
        for n_cal in calibration_sizes:
            for bin_name, predicate in bins:
                subset = [row for row in rare_rows if row["scenario"] == scenario_name and row["n_cal"] == n_cal and predicate(int(row["own_calibration_count"]))]
                for method in METHODS:
                    method_rows = [row for row in subset if row["method"] == method]
                    if method_rows:
                        rare_summary.append({"scenario": scenario_name, "n_cal": n_cal, "support_bin": bin_name, "method": method,
                                             "repetitions": len(method_rows), "finite_threshold_rate": 1 - mean(int(v["threshold_is_infinite"]) for v in method_rows),
                                             "class4_coverage": mean(float(v["coverage"]) for v in method_rows),
                                             "mean_selected_radius": mean(int(v["selected_radius"]) for v in method_rows),
                                             "mean_certified_epsilon": mean(float(v["certified_epsilon"]) for v in method_rows),
                                             "mean_pooled_support": mean(int(v["pooled_calibration_count"]) for v in method_rows)})
    write_csv(args.output_dir / "rare_support_summary.csv", rare_summary)
    certificate_summary = []
    pair_groups: dict[tuple[str, int, int], list[dict[str, object]]] = defaultdict(list)
    for row in pair_rows: pair_groups[(str(row["scenario"]), int(row["class_j"]), int(row["class_k"]))].append(row)
    for (scenario, first, second), values in sorted(pair_groups.items()):
        certificate_summary.append({"scenario": scenario, "class_j": first, "class_k": second, "repetitions": len(values),
                                    "true_ks": values[0]["true_ks"], "per_pair_certificate_coverage": mean(int(v["certificate_covers_true_ks"]) for v in values),
                                    "mean_direct_certificate": mean(float(v["direct_certificate"]) for v in values), "mean_path_certificate": mean(float(v["path_certificate"]) for v in values),
                                    "mean_final_certificate": mean(float(v["final_certificate"]) for v in values),
                                    "simultaneous_certificate_coverage": None, "structural_certificate_failures": None})
    # all-pair status is repeated while pairs are built, so reconstruct it safely per repetition.
    failures = defaultdict(int)
    for row in pair_rows:
        if not int(row["certificate_covers_true_ks"]): failures[(row["scenario"], row["n_cal"], row["repetition"])] += 1
    repetitions_total = len({(r['scenario'], r['n_cal'], r['repetition']) for r in pair_rows})
    certificate_summary.append({"scenario": "ALL", "class_j": "ALL", "class_k": "ALL", "repetitions": repetitions_total,
                                "true_ks": None, "per_pair_certificate_coverage": None, "mean_direct_certificate": None, "mean_path_certificate": None, "mean_final_certificate": None,
                                "simultaneous_certificate_coverage": 1 - len(failures) / len({(r['scenario'], r['n_cal'], r['repetition']) for r in pair_rows}), "structural_certificate_failures": sum(failures.values())})
    write_csv(args.output_dir / "structural_certificate_summary.csv", certificate_summary)
    radius_summary = []
    for (scenario, n_cal, method, class_id), values in sorted(grouped.items()):
        if method.startswith("adaptive"):
            radius_summary.append({"scenario": scenario, "n_cal": n_cal, "method": method, "class_id": class_id,
                                   "radius_0_rate": mean(int(v["selected_radius"]) == 0 for v in values), "radius_1_rate": mean(int(v["selected_radius"]) == 1 for v in values), "radius_2_rate": mean(int(v["selected_radius"]) == 2 for v in values)})
    write_csv(args.output_dir / "selected_radius_summary.csv", radius_summary)


if __name__ == "__main__":
    main()
