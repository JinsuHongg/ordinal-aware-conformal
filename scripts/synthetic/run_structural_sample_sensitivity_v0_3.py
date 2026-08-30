#!/usr/bin/env python3
"""Measure v0.3 sensitivity to structural-sample size without changing v0.3."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from collections import defaultdict
from math import isinf
from pathlib import Path
from statistics import mean, median, stdev

import numpy as np

from ordinal_aware_conformal.calibration.adaptive_ordinal_borrowing import (
    fit_adaptive_ordinal_borrowing, fit_independent_mondrian,
    ordinal_neighborhood, select_neighborhoods, structural_certificates,
)
from ordinal_aware_conformal.synthetic.ordinal_borrowing_generator import SCENARIOS, draw_population, true_ks_matrix


STRUCTURAL_SIZES = (500, 1_000, 2_000, 5_000, 10_000, 20_000, 50_000)


def git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def descriptive(values: list[float], prefix: str) -> dict[str, float]:
    ordered = np.asarray(values, dtype=float)
    return {f"mean_{prefix}": float(ordered.mean()), f"median_{prefix}": float(np.median(ordered)),
            f"sd_{prefix}": float(ordered.std(ddof=1)) if len(ordered) > 1 else 0.0,
            f"p10_{prefix}": float(np.quantile(ordered, 0.10)), f"p90_{prefix}": float(np.quantile(ordered, 0.90)),
            f"min_{prefix}": float(ordered.min()), f"max_{prefix}": float(ordered.max())}


def write_svg(path: Path, title: str, y_label: str, series: dict[str, list[tuple[int, float]]], log_x: bool = True) -> None:
    width, height, left, bottom = 760, 460, 85, 65
    all_points = [point for values in series.values() for point in values]
    xs, ys = [point[0] for point in all_points], [point[1] for point in all_points]
    transform_x = (lambda value: np.log10(value)) if log_x else (lambda value: value)
    x_min, x_max = transform_x(min(xs)), transform_x(max(xs))
    y_min, y_max = min(0.0, min(ys)), max(ys)
    if y_max == y_min: y_max += 1.0
    def x(value: float) -> float: return left + (width - left - 35) * (transform_x(value) - x_min) / max(1e-12, x_max - x_min)
    def y(value: float) -> float: return height - bottom - (height - bottom - 55) * (value - y_min) / (y_max - y_min)
    colors = ("#1f77b4", "#ff7f0e", "#2ca02c", "#d62728")
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="white"/>', f'<text x="{left}" y="28" font-size="18" font-family="sans-serif">{title}</text>', f'<line x1="{left}" y1="55" x2="{left}" y2="{height-bottom}" stroke="black"/><line x1="{left}" y1="{height-bottom}" x2="{width-35}" y2="{height-bottom}" stroke="black"/>']
    for tick in range(5):
        value = y_min + tick * (y_max - y_min) / 4
        parts.append(f'<text x="8" y="{y(value)+4:.1f}" font-size="11" font-family="sans-serif">{value:.3f}</text>')
    for value in xs:
        if value in sorted(set(xs)):
            parts.append(f'<text x="{x(value)-10:.1f}" y="{height-bottom+20}" font-size="11" font-family="sans-serif">{value:g}</text>')
    parts.append(f'<text x="{width/2-92}" y="{height-12}" font-size="13" font-family="sans-serif">structural sample size (log scale)</text><text x="18" y="{height/2}" transform="rotate(-90 18 {height/2})" font-size="13" font-family="sans-serif">{y_label}</text>')
    for index, (name, values) in enumerate(series.items()):
        color = colors[index % len(colors)]
        ordered = sorted(values)
        parts.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.5" points="{" ".join(f"{x(a):.1f},{y(b):.1f}" for a,b in ordered)}"/>')
        parts.extend(f'<circle cx="{x(a):.1f}" cy="{y(b):.1f}" r="3.5" fill="{color}"/>' for a, b in ordered)
        parts.append(f'<text x="{width-245}" y="{55+22*index}" font-size="12" font-family="sans-serif" fill="{color}">{name}</text>')
    parts.append('</svg>')
    path.write_text("\n".join(parts))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/synthetic_structural_sample_sensitivity_v0_3"))
    parser.add_argument("--repetitions", type=int, default=100)
    parser.add_argument("--test-size", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=20260828)
    parser.add_argument("--structural-sizes", type=int, nargs="+", default=STRUCTURAL_SIZES)
    args = parser.parse_args()
    n_classes, alpha, delta_str, n_cal, rare_class = 5, 0.10, 0.05, 200, 4
    probabilities, scenario = (0.30, 0.25, 0.22, 0.20, 0.03), SCENARIOS["strong_smoothness"]
    config: dict[str, object] = {"study": "structural_sample_sensitivity_v0_3", "method_version": "candidate-v0.3-unchanged",
        "scenario": scenario.name, "means": scenario.means, "sigma": scenario.sigma, "n_classes": n_classes, "alpha": alpha,
        "delta_str": delta_str, "class_probabilities": probabilities, "rare_class": rare_class, "n_cal": n_cal,
        "n_test": args.test_size, "structural_sizes": args.structural_sizes, "repetitions": args.repetitions, "seed": args.seed,
        "final_calibration_sampling": "ordinary i.i.d. population sample; not fixed-count or stratified",
        "coupling": "within a repetition, calibration and test draws are shared across n_str; each n_str receives an independent structural draw",
        "candidate_radii": [0, 1, 2], "score": "unchanged direct true-label Normal score generator"}
    config["config_hash"] = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest(); config["code_commit"] = git_commit()
    args.output_dir.mkdir(parents=True, exist_ok=True); (args.output_dir / "plots").mkdir(exist_ok=True)
    (args.output_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    truth, rows, pair_rows = true_ks_matrix(scenario), [], []
    for repetition in range(args.repetitions):
        calibration_rng = np.random.default_rng(args.seed + 1_000_000 + repetition)
        test_rng = np.random.default_rng(args.seed + 2_000_000 + repetition)
        calibration_labels, calibration_scores = draw_population(calibration_rng, n_cal, probabilities, scenario)
        test_labels, test_scores = draw_population(test_rng, args.test_size, probabilities, scenario)
        class4_test = test_scores[test_labels == rare_class]
        for n_str in args.structural_sizes:
            structural_rng = np.random.default_rng(args.seed + n_str * 10_000 + repetition)
            structural_labels, structural_scores = draw_population(structural_rng, n_str, probabilities, scenario)
            certificates = structural_certificates(structural_labels, structural_scores, n_classes, delta_str)
            selection = select_neighborhoods(certificates, n_cal, alpha)
            mondrian = fit_independent_mondrian(calibration_labels, calibration_scores, alpha, n_classes)
            approximate = fit_adaptive_ordinal_borrowing(calibration_labels, calibration_scores, alpha, n_classes, selection, certified=False)
            certified = fit_adaptive_ordinal_borrowing(calibration_labels, calibration_scores, alpha, n_classes, selection, certified=True)
            candidate_eps = []
            for radius in (0, 1, 2):
                candidate_eps.append(max(certificates.delta[rare_class][member] for member in ordinal_neighborhood(rare_class, radius, n_classes)))
            def coverage(result: object) -> float:
                threshold = result.thresholds[rare_class]  # type: ignore[attr-defined]
                return 1.0 if isinf(threshold) else float(np.mean(class4_test <= threshold))
            rows.append({"n_str": n_str, "repetition": repetition, "m4": certificates.counts[rare_class], "e4": certificates.dkw_radii[rare_class],
                         "n4": mondrian.own_support[rare_class], "h4": selection.radii[rare_class], "epsilon4": selection.epsilons[rare_class],
                         "epsilon4_h0": candidate_eps[0], "epsilon4_h1": candidate_eps[1], "epsilon4_h2": candidate_eps[2],
                         "alpha_minus_epsilon4": alpha - selection.epsilons[rare_class], "N4_star": certified.pooled_support[rare_class],
                         "mondrian_rank": mondrian.ranks[rare_class], "approx_rank": approximate.ranks[rare_class], "certified_rank": certified.ranks[rare_class],
                         "mondrian_finite": int(not isinf(mondrian.thresholds[rare_class])), "approx_finite": int(not isinf(approximate.thresholds[rare_class])),
                         "certified_finite": int(not isinf(certified.thresholds[rare_class])), "mondrian_coverage": coverage(mondrian),
                         "approx_coverage": coverage(approximate), "certified_coverage": coverage(certified)})
            covered_all = True
            for first in range(n_classes):
                for second in range(first + 1, n_classes):
                    covered = truth[first][second] <= certificates.delta[first][second]; covered_all &= covered
                    pair_rows.append({"n_str": n_str, "repetition": repetition, "class_j": first, "class_k": second, "true_ks": truth[first][second],
                                      "final_certificate": certificates.delta[first][second], "certificate_covers_true_ks": int(covered),
                                      "simultaneous_certificate_covers_all_pairs": int(covered_all)})
    write_csv(args.output_dir / "per_repetition.csv", rows); write_csv(args.output_dir / "pairwise_certificate_summary.csv", pair_rows)
    summary = []
    for n_str in args.structural_sizes:
        values = [row for row in rows if row["n_str"] == n_str]
        item: dict[str, object] = {"n_str": n_str, "repetitions": len(values), **descriptive([float(v["m4"]) for v in values], "m4"),
            "p_m4_zero": mean(int(v["m4"]) == 0 for v in values), **descriptive([float(v["e4"]) for v in values], "e4"),
            **descriptive([float(v["epsilon4"]) for v in values], "epsilon4"), "mean_h4": mean(int(v["h4"]) for v in values),
            "p_h4_0": mean(int(v["h4"]) == 0 for v in values), "p_h4_1": mean(int(v["h4"]) == 1 for v in values), "p_h4_2": mean(int(v["h4"]) == 2 for v in values),
            "admissible_h0_rate": mean(float(v["epsilon4_h0"]) < alpha for v in values), "admissible_h1_rate": mean(float(v["epsilon4_h1"]) < alpha for v in values), "admissible_h2_rate": mean(float(v["epsilon4_h2"]) < alpha for v in values),
            "mondrian_finite_rate": mean(int(v["mondrian_finite"]) for v in values), "approx_finite_rate": mean(int(v["approx_finite"]) for v in values), "certified_finite_rate": mean(int(v["certified_finite"]) for v in values),
            "certified_finite_improvement": mean(int(v["certified_finite"]) - int(v["mondrian_finite"]) for v in values),
            "mondrian_class4_coverage": mean(float(v["mondrian_coverage"]) for v in values), "approx_class4_coverage": mean(float(v["approx_coverage"]) for v in values), "certified_class4_coverage": mean(float(v["certified_coverage"]) for v in values),
            "mean_pooled_support": mean(int(v["N4_star"]) for v in values), "mean_alpha_minus_epsilon4": mean(float(v["alpha_minus_epsilon4"]) for v in values)}
        summary.append(item)
    write_csv(args.output_dir / "summary_by_n_str.csv", summary)
    rare_summary = []
    bins = (("n4_le_5", lambda count: count <= 5), ("n4_6_10", lambda count: 6 <= count <= 10), ("n4_gt_10", lambda count: count > 10))
    for n_str in args.structural_sizes:
        for name, predicate in bins:
            values = [row for row in rows if row["n_str"] == n_str and predicate(int(row["n4"]))]
            if values:
                rare_summary.append({"n_str": n_str, "support_bin": name, "repetitions": len(values), "mondrian_finite_rate": mean(int(v["mondrian_finite"]) for v in values),
                    "certified_finite_rate": mean(int(v["certified_finite"]) for v in values), "certified_class4_coverage": mean(float(v["certified_coverage"]) for v in values),
                    "mean_h4": mean(int(v["h4"]) for v in values), "mean_epsilon4": mean(float(v["epsilon4"]) for v in values)})
    write_csv(args.output_dir / "rare_support_summary.csv", rare_summary)
    certificate_summary = []
    for n_str in args.structural_sizes:
        values = [row for row in pair_rows if row["n_str"] == n_str]
        failures = {int(row["repetition"]) for row in values if not int(row["certificate_covers_true_ks"])}
        certificate_summary.append({"n_str": n_str, "pairwise_certificate_coverage": mean(int(v["certificate_covers_true_ks"]) for v in values),
            "simultaneous_certificate_coverage": 1 - len(failures) / args.repetitions, "structural_certificate_failures": len(failures),
            "empirical_structural_failure_probability": len(failures) / args.repetitions})
    write_csv(args.output_dir / "structural_certificate_summary.csv", certificate_summary)
    plot_dir = args.output_dir / "plots"
    write_svg(plot_dir / "epsilon4_vs_n_str.svg", "Certified class-4 discrepancy", "mean epsilon_4*", {"certified epsilon": [(int(r["n_str"]), float(r["mean_epsilon4"])) for r in summary]})
    write_svg(plot_dir / "borrowing_probability_vs_n_str.svg", "Class-4 positive-radius selection", "P(h_4*>0)", {"positive radius": [(int(r["n_str"]), 1 - float(r["p_h4_0"])) for r in summary]})
    write_svg(plot_dir / "finite_rate_vs_n_str.svg", "Class-4 finite-threshold rate", "finite rate", {"Mondrian": [(int(r["n_str"]), float(r["mondrian_finite_rate"])) for r in summary], "Approximate": [(int(r["n_str"]), float(r["approx_finite_rate"])) for r in summary], "Certified": [(int(r["n_str"]), float(r["certified_finite_rate"])) for r in summary]})
    write_svg(plot_dir / "coverage_vs_n_str.svg", "Class-4 coverage", "coverage", {"Mondrian": [(int(r["n_str"]), float(r["mondrian_class4_coverage"])) for r in summary], "Approximate": [(int(r["n_str"]), float(r["approx_class4_coverage"])) for r in summary], "Certified": [(int(r["n_str"]), float(r["certified_class4_coverage"])) for r in summary]})


if __name__ == "__main__":
    main()
