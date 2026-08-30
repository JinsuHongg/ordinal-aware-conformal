#!/usr/bin/env python3
"""Certificate-only comparison: v0.3 DKW against direct two-sample KS."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path
from statistics import mean, median

import numpy as np

from ordinal_aware_conformal.calibration.adaptive_ordinal_borrowing import structural_certificates
from ordinal_aware_conformal.calibration.two_sample_ks_certificate import two_sample_structural_certificates
from ordinal_aware_conformal.synthetic.ordinal_borrowing_generator import SCENARIOS, draw_population, true_ks_matrix


SIZES = (500, 1_000, 2_000, 5_000, 10_000, 20_000, 50_000)


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def _commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _write_svg(path: Path, title: str, y_label: str, series: dict[str, list[tuple[int, float]]]) -> None:
    width, height, left, bottom = 760, 440, 80, 65
    points = [point for values in series.values() for point in values]
    x_values, y_values = [np.log10(point[0]) for point in points], [point[1] for point in points]
    x_min, x_max, y_min, y_max = min(x_values), max(x_values), min(0.0, min(y_values)), max(y_values)
    if y_max == y_min: y_max += 1.0
    x = lambda value: left + (width-left-35)*(np.log10(value)-x_min)/(x_max-x_min)
    y = lambda value: height-bottom-(height-bottom-45)*(value-y_min)/(y_max-y_min)
    colors = ("#1f77b4", "#d62728", "#2ca02c")
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">', '<rect width="100%" height="100%" fill="white"/>', f'<text x="{left}" y="28" font-size="18" font-family="sans-serif">{title}</text>', f'<line x1="{left}" y1="45" x2="{left}" y2="{height-bottom}" stroke="black"/><line x1="{left}" y1="{height-bottom}" x2="{width-35}" y2="{height-bottom}" stroke="black"/>']
    for value in sorted(set(point[0] for point in points)):
        parts.append(f'<text x="{x(value)-12:.1f}" y="{height-bottom+18}" font-size="10" font-family="sans-serif">{value:g}</text>')
    for index, (name, values) in enumerate(series.items()):
        color = colors[index]
        ordered = sorted(values)
        parts.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.5" points="{" ".join(f"{x(a):.1f},{y(b):.1f}" for a,b in ordered)}"/>')
        parts.extend(f'<circle cx="{x(a):.1f}" cy="{y(b):.1f}" r="3" fill="{color}"/>' for a, b in ordered)
        parts.append(f'<text x="{width-250}" y="{55+18*index}" font-size="12" font-family="sans-serif" fill="{color}">{name}</text>')
    parts.extend([f'<text x="{width/2-100}" y="{height-10}" font-size="12" font-family="sans-serif">structural sample size (log scale)</text>', f'<text x="16" y="{height/2}" transform="rotate(-90 16 {height/2})" font-size="12" font-family="sans-serif">{y_label}</text>', '</svg>'])
    path.write_text("\n".join(parts))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/synthetic_two_sample_ks_certificate"))
    parser.add_argument("--repetitions", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260828)
    parser.add_argument("--structural-sizes", type=int, nargs="+", default=SIZES)
    args = parser.parse_args()
    n_classes, alpha, delta_str = 5, 0.10, 0.05
    probabilities, scenario = (0.30, 0.25, 0.22, 0.20, 0.03), SCENARIOS["strong_smoothness"]
    config = {"study": "direct_two_sample_ks_certificate_comparison", "scenario": scenario.name, "n_classes": n_classes, "alpha": alpha, "delta_str": delta_str, "pairwise_delta": delta_str / 10, "class_probabilities": probabilities, "structural_sizes": args.structural_sizes, "repetitions": args.repetitions, "seed": args.seed, "true_ks": "exact equal-variance normal-location formula", "two_sample_bound": "Underwood and Paillusson (2024) Proposition 2b / equation (11), numerically inverted"}
    config["config_hash"] = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest(); config["code_commit"] = _commit()
    args.output_dir.mkdir(parents=True, exist_ok=True); (args.output_dir / "plots").mkdir(exist_ok=True)
    (args.output_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    truth, rows = true_ks_matrix(scenario), []
    for n_str in args.structural_sizes:
        for repetition in range(args.repetitions):
            rng = np.random.default_rng(args.seed + n_str * 10_000 + repetition)
            labels, scores = draw_population(rng, n_str, probabilities, scenario)
            dkw, two_sample = structural_certificates(labels, scores, n_classes, delta_str), two_sample_structural_certificates(labels, scores, n_classes, delta_str)
            dkw_all, two_all = True, True
            for first in range(n_classes):
                for second in range(first + 1, n_classes):
                    dkw_cover = truth[first][second] <= dkw.delta[first][second]
                    two_cover = truth[first][second] <= two_sample.delta[first][second]
                    dkw_all &= dkw_cover; two_all &= two_cover
                    rows.append({"n_str": n_str, "repetition": repetition, "class_j": first, "class_k": second, "m_j": dkw.counts[first], "m_k": dkw.counts[second], "true_ks": truth[first][second], "empirical_ks": dkw.empirical_ks[first][second], "dkw_ucb": dkw.delta[first][second], "two_sample_radius": two_sample.pairwise_radii[first][second], "two_sample_direct_ucb": two_sample.direct[first][second], "two_sample_path_ucb": two_sample.path[first][second], "two_sample_ucb": two_sample.delta[first][second], "ucb_reduction": dkw.delta[first][second] - two_sample.delta[first][second], "dkw_covers": int(dkw_cover), "two_sample_covers": int(two_cover), "dkw_all_pairs_cover": int(dkw_all), "two_sample_all_pairs_cover": int(two_all)})
    _write_csv(args.output_dir / "certificate_per_repetition.csv", rows)
    summaries = []
    for n_str in args.structural_sizes:
        values = [row for row in rows if row["n_str"] == n_str]
        primary = [row for row in values if row["class_j"] == 3 and row["class_k"] == 4]
        dkw_failed = {int(row["repetition"]) for row in values if not int(row["dkw_covers"])}
        two_failed = {int(row["repetition"]) for row in values if not int(row["two_sample_covers"])}
        summaries.append({"n_str": n_str, "mean_m3": mean(float(row["m_j"]) for row in primary), "mean_m4": mean(float(row["m_k"]) for row in primary), "true_ks_34": primary[0]["true_ks"], "mean_empirical_ks_34": mean(float(row["empirical_ks"]) for row in primary), "mean_dkw_ucb_34": mean(float(row["dkw_ucb"]) for row in primary), "mean_two_sample_ucb_34": mean(float(row["two_sample_ucb"]) for row in primary), "mean_ucb_reduction_34": mean(float(row["ucb_reduction"]) for row in primary), "median_ucb_reduction_34": median(float(row["ucb_reduction"]) for row in primary), "p_dkw_34_below_alpha": mean(float(row["dkw_ucb"]) < alpha for row in primary), "p_two_sample_34_below_alpha": mean(float(row["two_sample_ucb"]) < alpha for row in primary), "dkw_pairwise_coverage": mean(int(row["dkw_covers"]) for row in values), "two_sample_pairwise_coverage": mean(int(row["two_sample_covers"]) for row in values), "dkw_simultaneous_coverage": 1 - len(dkw_failed) / args.repetitions, "two_sample_simultaneous_coverage": 1 - len(two_failed) / args.repetitions})
    _write_csv(args.output_dir / "certificate_summary.csv", summaries)
    pairwise = []
    for n_str in args.structural_sizes:
        for first in range(n_classes):
            for second in range(first + 1, n_classes):
                values = [row for row in rows if row["n_str"] == n_str and row["class_j"] == first and row["class_k"] == second]
                pairwise.append({"n_str": n_str, "class_j": first, "class_k": second, "true_ks": values[0]["true_ks"], "dkw_pairwise_coverage": mean(int(row["dkw_covers"]) for row in values), "two_sample_pairwise_coverage": mean(int(row["two_sample_covers"]) for row in values), "mean_dkw_ucb": mean(float(row["dkw_ucb"]) for row in values), "mean_two_sample_ucb": mean(float(row["two_sample_ucb"]) for row in values), "mean_ucb_reduction": mean(float(row["ucb_reduction"]) for row in values)})
    _write_csv(args.output_dir / "pairwise_summary.csv", pairwise)
    plot = args.output_dir / "plots"
    _write_svg(plot / "ucb_34_vs_n_str.svg", "Class 3--4 certificates", "mean UCB", {"DKW": [(int(row["n_str"]), float(row["mean_dkw_ucb_34"])) for row in summaries], "two-sample": [(int(row["n_str"]), float(row["mean_two_sample_ucb_34"])) for row in summaries], "true KS": [(int(row["n_str"]), float(row["true_ks_34"])) for row in summaries]})
    _write_svg(plot / "admissibility_34_vs_n_str.svg", "Class 3--4 admissibility", "P(U_34 < alpha)", {"DKW": [(int(row["n_str"]), float(row["p_dkw_34_below_alpha"])) for row in summaries], "two-sample": [(int(row["n_str"]), float(row["p_two_sample_34_below_alpha"])) for row in summaries]})


if __name__ == "__main__":
    main()
