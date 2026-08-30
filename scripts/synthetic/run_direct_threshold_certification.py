#!/usr/bin/env python3
"""Minimal feasibility study for ordinal proposals plus target-class PAC tests."""
from __future__ import annotations

import argparse
import csv
import json
from math import ceil, erf, inf, isinf, sqrt
from pathlib import Path
from statistics import mean, stdev

import numpy as np

from ordinal_aware_conformal.calibration.direct_threshold_certification import (
    certify_fixed_threshold,
    direct_pac_threshold,
    exact_acceptance_probability,
    minimum_successes_for_certification,
    proposal_quantile,
)
from ordinal_aware_conformal.synthetic.ordinal_borrowing_generator import SCENARIOS, draw_population


TAUS = (0.90, 0.93, 0.95, 0.97)
CERTIFICATION_SIZES = (1_000, 2_000, 5_000, 10_000, 20_000)
ACCEPTANCE_COUNTS = (30, 60, 150, 300, 600)
ACCEPTANCE_COVERAGES = (0.90, 0.92, 0.93, 0.95, 0.97, 0.99)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def normal_cdf(value: float, mean_value: float, sigma: float) -> float:
    if isinf(value):
        return 1.0
    return 0.5 * (1.0 + erf((value - mean_value) / (sqrt(2.0) * sigma)))


def mondrian_threshold(scores: np.ndarray, alpha: float) -> float:
    rank = ceil((len(scores) + 1) * (1.0 - alpha))
    return inf if rank > len(scores) else float(np.sort(scores)[rank - 1])


def finite(value: float) -> int:
    return int(not isinf(value))


def threshold_value(value: float) -> float | None:
    return None if isinf(value) else value


def add_method_row(rows: list[dict[str, object]], *, repetition: int, n_cert: int, method: str, tau: float | None,
                   result_threshold: float, support: int, successes: int | None, lower_bound: float | None,
                   candidate: float | None, candidate_coverage: float | None, scenario_mean: float, sigma: float) -> None:
    output_coverage = normal_cdf(result_threshold, scenario_mean, sigma)
    rows.append({
        "repetition": repetition, "n_cert": n_cert, "method": method, "tau": tau,
        "candidate_threshold": None if candidate is None else threshold_value(candidate),
        "candidate_true_coverage": candidate_coverage,
        "threshold": threshold_value(result_threshold), "finite": finite(result_threshold),
        "true_coverage": output_coverage, "pac_valid": int(output_coverage >= 0.90),
        "support": support, "successes": successes, "lower_bound": lower_bound,
        "accepted": None if lower_bound is None else int(not isinf(result_threshold)),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/synthetic_direct_threshold_certification"))
    parser.add_argument("--repetitions", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260828)
    args = parser.parse_args()

    alpha, target_coverage, delta_cert, n_classes = 0.10, 0.90, 0.05, 5
    delta_k, n_prop, target, neighbor = delta_cert / n_classes, 200, 4, 3
    probabilities, scenario = (0.30, 0.25, 0.22, 0.20, 0.03), SCENARIOS["strong_smoothness"]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "study": "direct_class_conditional_threshold_certification", "alpha": alpha,
        "target_coverage": target_coverage, "delta_cert": delta_cert, "delta_k": delta_k,
        "n_classes": n_classes, "probabilities": probabilities, "scenario": scenario.name,
        "target_class": target, "fixed_neighborhood": [neighbor, target], "n_prop": n_prop,
        "n_cert_grid": CERTIFICATION_SIZES, "taus": TAUS, "repetitions": args.repetitions,
        "seed": args.seed, "candidate_rule": "ceil((N+1)*tau) pooled proposal order statistic; +infinity if rank>N",
        "certification_rule": "one-sided Clopper-Pearson lower bound, accept if L>=0.90",
        "direct_pac_rule": "smallest target-score order statistic whose one-sided Clopper-Pearson lower bound is >=0.90",
    }
    (args.output_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")

    acceptance_rows = []
    for support in ACCEPTANCE_COUNTS:
        required = minimum_successes_for_certification(support, target_coverage, delta_k)
        for coverage in ACCEPTANCE_COVERAGES:
            acceptance_rows.append({"certification_support": support, "true_coverage": coverage,
                                    "minimum_successes": required, "acceptance_probability": exact_acceptance_probability(support, coverage, target_coverage, delta_k)})
    write_csv(args.output_dir / "exact_binomial_acceptance_table.csv", acceptance_rows)

    rows: list[dict[str, object]] = []
    for n_cert in CERTIFICATION_SIZES:
        for repetition in range(args.repetitions):
            proposal_rng = np.random.default_rng(args.seed + n_cert * 10_000 + repetition)
            cert_rng = np.random.default_rng(args.seed + 900_000_000 + n_cert * 10_000 + repetition)
            prop_labels, prop_scores = draw_population(proposal_rng, n_prop, probabilities, scenario)
            cert_labels, cert_scores = draw_population(cert_rng, n_cert, probabilities, scenario)
            proposal_pool = prop_scores[(prop_labels == neighbor) | (prop_labels == target)]
            prop_target = prop_scores[prop_labels == target]
            cert_target = cert_scores[cert_labels == target]
            all_target = np.concatenate((prop_target, cert_target))

            mondrian = mondrian_threshold(all_target, alpha)
            add_method_row(rows, repetition=repetition, n_cert=n_cert, method="independent_mondrian_total_budget", tau=None,
                           result_threshold=mondrian, support=len(all_target), successes=None, lower_bound=None,
                           candidate=None, candidate_coverage=None, scenario_mean=scenario.means[target], sigma=scenario.sigma)

            split_direct = direct_pac_threshold(cert_target, target_coverage, delta_k)
            add_method_row(rows, repetition=repetition, n_cert=n_cert, method="direct_pac_split_matched", tau=None,
                           result_threshold=split_direct.threshold, support=split_direct.support, successes=split_direct.successes,
                           lower_bound=split_direct.lower_bound, candidate=split_direct.candidate,
                           candidate_coverage=normal_cdf(split_direct.candidate, scenario.means[target], scenario.sigma),
                           scenario_mean=scenario.means[target], sigma=scenario.sigma)
            total_direct = direct_pac_threshold(all_target, target_coverage, delta_k)
            add_method_row(rows, repetition=repetition, n_cert=n_cert, method="direct_pac_total_budget", tau=None,
                           result_threshold=total_direct.threshold, support=total_direct.support, successes=total_direct.successes,
                           lower_bound=total_direct.lower_bound, candidate=total_direct.candidate,
                           candidate_coverage=normal_cdf(total_direct.candidate, scenario.means[target], scenario.sigma),
                           scenario_mean=scenario.means[target], sigma=scenario.sigma)

            for tau in TAUS:
                candidate = proposal_quantile(proposal_pool, tau)
                candidate_coverage = normal_cdf(candidate, scenario.means[target], scenario.sigma)
                add_method_row(rows, repetition=repetition, n_cert=n_cert, method="ordinal_pooled_candidate_uncertified", tau=tau,
                               result_threshold=candidate, support=len(proposal_pool), successes=None, lower_bound=None,
                               candidate=candidate, candidate_coverage=candidate_coverage,
                               scenario_mean=scenario.means[target], sigma=scenario.sigma)
                certified = certify_fixed_threshold(candidate, cert_target, target_coverage, delta_k)
                add_method_row(rows, repetition=repetition, n_cert=n_cert, method="ordinal_candidate_plus_cp_certification", tau=tau,
                               result_threshold=certified.threshold, support=certified.support, successes=certified.successes,
                               lower_bound=certified.lower_bound, candidate=candidate, candidate_coverage=candidate_coverage,
                               scenario_mean=scenario.means[target], sigma=scenario.sigma)
    write_csv(args.output_dir / "per_repetition.csv", rows)

    summary = []
    keys = sorted({(row["n_cert"], row["method"], row["tau"]) for row in rows}, key=lambda item: (item[0], item[1], str(item[2])))
    for n_cert, method, tau in keys:
        values = [row for row in rows if (row["n_cert"], row["method"], row["tau"]) == (n_cert, method, tau)]
        finite_thresholds = [float(row["threshold"]) for row in values if row["threshold"] is not None]
        candidate_coverages = [float(row["candidate_true_coverage"]) for row in values if row["candidate_true_coverage"] is not None]
        summary.append({"n_cert": n_cert, "method": method, "tau": tau, "repetitions": len(values),
                        "mean_support": mean(float(row["support"]) for row in values), "finite_rate": mean(int(row["finite"]) for row in values),
                        "pac_valid_rate": mean(int(row["pac_valid"]) for row in values),
                        "mean_true_coverage": mean(float(row["true_coverage"]) for row in values),
                        "mean_threshold_finite": mean(finite_thresholds) if finite_thresholds else None,
                        "mean_candidate_true_coverage": mean(candidate_coverages) if candidate_coverages else None,
                        "sd_candidate_true_coverage": stdev(candidate_coverages) if len(candidate_coverages) > 1 else None,
                        "mean_lower_bound": mean(float(row["lower_bound"]) for row in values if row["lower_bound"] is not None) if any(row["lower_bound"] is not None for row in values) else None,
                        "mean_successes": mean(float(row["successes"]) for row in values if row["successes"] is not None) if any(row["successes"] is not None for row in values) else None})
    write_csv(args.output_dir / "summary.csv", summary)
    candidate_summary = [row for row in summary if row["method"] == "ordinal_pooled_candidate_uncertified"]
    write_csv(args.output_dir / "candidate_margin_summary.csv", candidate_summary)
    comparisons = []
    for n_cert in CERTIFICATION_SIZES:
        total = next(row for row in summary if row["n_cert"] == n_cert and row["method"] == "direct_pac_total_budget")
        split = next(row for row in summary if row["n_cert"] == n_cert and row["method"] == "direct_pac_split_matched")
        for tau in TAUS:
            certified = next(row for row in summary if row["n_cert"] == n_cert and row["method"] == "ordinal_candidate_plus_cp_certification" and row["tau"] == tau)
            comparisons.append({"n_cert": n_cert, "tau": tau, "ordinal_certified_finite_rate": certified["finite_rate"],
                                "direct_pac_split_finite_rate": split["finite_rate"], "direct_pac_total_finite_rate": total["finite_rate"],
                                "vs_split_finite_rate_difference": certified["finite_rate"] - split["finite_rate"],
                                "vs_total_finite_rate_difference": certified["finite_rate"] - total["finite_rate"],
                                "ordinal_mean_finite_threshold": certified["mean_threshold_finite"],
                                "direct_total_mean_threshold": total["mean_threshold_finite"]})
    write_csv(args.output_dir / "equal_budget_comparison.csv", comparisons)


if __name__ == "__main__":
    main()
