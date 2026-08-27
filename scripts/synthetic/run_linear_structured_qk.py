#!/usr/bin/env python3
"""Run the minimal synthetic validation of linear structured q_k.

This is an exploratory proof-of-concept.  It produces no canonical method
claim and does not use test outcomes to select any method setting.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import subprocess
from collections import defaultdict
from math import isinf
from pathlib import Path
from statistics import mean, pvariance
from typing import Iterable

from ordinal_aware_conformal.calibration.synthetic_linear import (
    CalibrationResult,
    fit_independent_mondrian,
    fit_linear_structured_mondrian,
    fit_ordinal_cluster,
)


METHODS = ("independent_mondrian", "ordinal_cluster", "linear_structured_final_mondrian")


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _draw_label(rng: random.Random, probabilities: list[float]) -> int:
    value, cumulative = rng.random(), 0.0
    for class_id, probability in enumerate(probabilities):
        cumulative += probability
        if value < cumulative:
            return class_id
    return len(probabilities) - 1


def _true_scores(rng: random.Random, labels: Iterable[int], base_noise: float, adjacent_noise_change: float) -> list[float]:
    """Generate |z-k| true-label scores from a fixed ordinal regression score.

    The latent prediction is z = Y + Normal(0, sigma_Y), so test candidate
    scores are |z-k|.  Increasing sigma by class gives neighboring classes
    related, but not identical, score distributions without training a model.
    """
    return [abs(rng.gauss(0.0, base_noise + adjacent_noise_change * label)) for label in labels]


def _candidate_scores(rng: random.Random, labels: list[int], n_classes: int, base_noise: float, adjacent_noise_change: float) -> list[list[float]]:
    rows = []
    for label in labels:
        latent = label + rng.gauss(0.0, base_noise + adjacent_noise_change * label)
        rows.append([abs(latent - candidate) for candidate in range(n_classes)])
    return rows


def _stratified_split(rng: random.Random, labels: list[int], scores: list[float], n_classes: int) -> tuple[list[int], list[float], list[int], list[float]]:
    structured_labels: list[int] = []
    structured_scores: list[float] = []
    final_labels: list[int] = []
    final_scores: list[float] = []
    grouped: list[list[float]] = [[] for _ in range(n_classes)]
    for label, score in zip(labels, scores, strict=True):
        grouped[label].append(score)
    for class_id, group in enumerate(grouped):
        rng.shuffle(group)
        split = len(group) // 2
        structured_labels.extend([class_id] * split)
        structured_scores.extend(group[:split])
        final_labels.extend([class_id] * (len(group) - split))
        final_scores.extend(group[split:])
    return structured_labels, structured_scores, final_labels, final_scores


def _prediction_metrics(candidate_scores: list[list[float]], labels: list[int], thresholds: tuple[float, ...], n_classes: int) -> dict[int, dict[str, float]]:
    by_class: dict[int, list[tuple[bool, int, int]]] = defaultdict(list)
    for row, label in zip(candidate_scores, labels, strict=True):
        prediction_set = [candidate for candidate, score in enumerate(row) if score <= thresholds[candidate]]
        span = prediction_set[-1] - prediction_set[0] + 1 if prediction_set else 0
        by_class[label].append((label in prediction_set, len(prediction_set), span))
    return {
        class_id: {
            "coverage": mean(item[0] for item in values),
            "mean_set_size": mean(item[1] for item in values),
            "mean_ordinal_span": mean(item[2] for item in values),
        }
        for class_id, values in by_class.items()
    }


def _finite_or_none(value: float) -> float | None:
    return None if isinf(value) else value


def _write_svg(path: Path, title: str, y_label: str, series: dict[str, list[tuple[int, float]]]) -> None:
    """Write a dependency-free line plot as SVG."""
    width, height, left, bottom = 760, 460, 85, 65
    points = [point for values in series.values() for point in values if point[1] == point[1] and not isinf(point[1])]
    x_values, y_values = [point[0] for point in points], [point[1] for point in points]
    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = min(0.0, min(y_values)), max(y_values)
    if y_max == y_min: y_max += 1.0
    def x(value: float) -> float: return left + (width - left - 35) * (value - x_min) / max(1, x_max - x_min)
    def y(value: float) -> float: return height - bottom - (height - bottom - 55) * (value - y_min) / (y_max - y_min)
    colors = {"independent_mondrian": "#1f77b4", "ordinal_cluster": "#ff7f0e", "linear_structured_final_mondrian": "#2ca02c"}
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="white"/>', f'<text x="{left}" y="28" font-size="18" font-family="sans-serif">{title}</text>', f'<line x1="{left}" y1="55" x2="{left}" y2="{height-bottom}" stroke="black"/><line x1="{left}" y1="{height-bottom}" x2="{width-35}" y2="{height-bottom}" stroke="black"/>']
    for tick in range(5):
        value = y_min + tick * (y_max - y_min) / 4
        parts.append(f'<text x="8" y="{y(value)+4:.1f}" font-size="11" font-family="sans-serif">{value:.3f}</text>')
    for value in sorted(set(x_values)):
        parts.append(f'<text x="{x(value)-8:.1f}" y="{height-bottom+20}" font-size="11" font-family="sans-serif">{value}</text>')
    parts.append(f'<text x="{width/2-85}" y="{height-12}" font-size="13" font-family="sans-serif">rare-class calibration count</text><text x="18" y="{height/2}" transform="rotate(-90 18 {height/2})" font-size="13" font-family="sans-serif">{y_label}</text>')
    for method, values in series.items():
        ordered = sorted(values)
        coords = " ".join(f"{x(a):.1f},{y(b):.1f}" for a, b in ordered)
        color = colors[method]
        parts.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.5" points="{coords}"/>')
        for a, b in ordered: parts.append(f'<circle cx="{x(a):.1f}" cy="{y(b):.1f}" r="3.5" fill="{color}"/>')
        parts.append(f'<text x="{width-245}" y="{55+22*list(series).index(method)}" font-size="12" font-family="sans-serif" fill="{color}">{method}</text>')
    parts.append('</svg>')
    path.write_text("\n".join(parts))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/synthetic_linear_structured_qk"))
    parser.add_argument("--repetitions", type=int, default=50)
    parser.add_argument("--test-size", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20260827)
    args = parser.parse_args()
    n_classes, alpha, rare_class = 5, 0.10, 0
    rare_counts = [100, 50, 20, 10, 5]
    class_probabilities = [0.05, 0.2375, 0.2375, 0.2375, 0.2375]
    config = {"study": "exploratory_minimal_synthetic_linear_structured_qk", "method_version": "exploratory-hard-split-v1", "n_classes": n_classes, "alpha": alpha, "rare_class": rare_class, "rare_counts": rare_counts, "other_class_calibration_count": 100, "class_probabilities": class_probabilities, "base_noise": 0.18, "adjacent_noise_change": 0.045, "structured_final_split": "stratified floor-half / remainder", "cluster_radius": 1, "repetitions": args.repetitions, "test_size": args.test_size, "seed": args.seed, "score": "S(x,k)=|z-k|; z=Y+Normal(0,sigma_Y)"}
    config["config_hash"] = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    config["code_commit"] = _git_commit()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    rows: list[dict[str, object]] = []
    for rare_count in rare_counts:
        for repetition in range(args.repetitions):
            rng = random.Random(args.seed + rare_count * 10_000 + repetition)
            labels = [class_id for class_id in range(n_classes) for _ in range(rare_count if class_id == rare_class else 100)]
            calibration_scores = _true_scores(rng, labels, config["base_noise"], config["adjacent_noise_change"])
            s_labels, s_scores, f_labels, f_scores = _stratified_split(rng, labels, calibration_scores, n_classes)
            results: dict[str, CalibrationResult] = {
                "independent_mondrian": fit_independent_mondrian(labels, calibration_scores, alpha, n_classes),
                "ordinal_cluster": fit_ordinal_cluster(labels, calibration_scores, alpha, n_classes),
                "linear_structured_final_mondrian": fit_linear_structured_mondrian(s_labels, s_scores, f_labels, f_scores, alpha, n_classes),
            }
            test_labels = [_draw_label(rng, class_probabilities) for _ in range(args.test_size)]
            test_scores = _candidate_scores(rng, test_labels, n_classes, config["base_noise"], config["adjacent_noise_change"])
            for method, result in results.items():
                metrics = _prediction_metrics(test_scores, test_labels, result.thresholds, n_classes)
                for class_id in range(n_classes):
                    class_metrics = metrics[class_id]
                    rows.append({"rare_count": rare_count, "repetition": repetition, "method": method, "class_id": class_id, "test_count": sum(label == class_id for label in test_labels), **class_metrics, "threshold": _finite_or_none(result.thresholds[class_id]), "threshold_is_infinite": int(isinf(result.thresholds[class_id])), "preliminary_threshold": None if result.preliminary_thresholds is None else _finite_or_none(result.preliminary_thresholds[class_id]), "correction": None if result.corrections is None else _finite_or_none(result.corrections[class_id]), "correction_is_infinite": 0 if result.corrections is None else int(isinf(result.corrections[class_id])), "final_support": None if result.final_support is None else result.final_support[class_id]})
    raw_path = args.output_dir / "per_run_results.csv"
    with raw_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    groups: dict[tuple[int, str, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows: groups[(int(row["rare_count"]), str(row["method"]), int(row["class_id"]))].append(row)
    summary: list[dict[str, object]] = []
    for (rare_count, method, class_id), values in sorted(groups.items()):
        finite_thresholds = [float(v["threshold"]) for v in values if v["threshold"] is not None]
        preliminary = [float(v["preliminary_threshold"]) for v in values if v["preliminary_threshold"] is not None]
        corrections = [abs(float(v["correction"])) for v in values if v["correction"] is not None]
        summary.append({"rare_count": rare_count, "method": method, "class_id": class_id, "mean_coverage": mean(float(v["coverage"]) for v in values), "mean_set_size": mean(float(v["mean_set_size"]) for v in values), "mean_ordinal_span": mean(float(v["mean_ordinal_span"]) for v in values), "threshold_variance": pvariance(finite_thresholds) if len(finite_thresholds) > 1 else None, "preliminary_threshold_variance": pvariance(preliminary) if len(preliminary) > 1 else None, "mean_abs_correction": mean(corrections) if corrections else None, "infinite_threshold_rate": mean(int(v["threshold_is_infinite"]) for v in values), "infinite_correction_rate": mean(int(v["correction_is_infinite"]) for v in values), "final_support": values[0]["final_support"]})
    summary_path = args.output_dir / "summary_by_class.csv"
    with summary_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(summary)
    aggregate: list[dict[str, object]] = []
    for rare_count in rare_counts:
        for method in METHODS:
            values = [row for row in rows if row["rare_count"] == rare_count and row["method"] == method]
            by_rep = defaultdict(list)
            for value in values: by_rep[int(value["repetition"])].append(value)
            aggregate.append({"rare_count": rare_count, "method": method, "marginal_coverage": mean(sum(float(v["coverage"]) * int(v["test_count"]) for v in run) / sum(int(v["test_count"]) for v in run) for run in by_rep.values()), "worst_class_coverage": mean(min(float(v["coverage"]) for v in run) for run in by_rep.values()), "rare_class_coverage": mean(float(v["coverage"]) for v in values if v["class_id"] == rare_class), "mean_set_size": mean(sum(float(v["mean_set_size"]) * int(v["test_count"]) for v in run) / sum(int(v["test_count"]) for v in run) for run in by_rep.values()), "mean_ordinal_span": mean(sum(float(v["mean_ordinal_span"]) * int(v["test_count"]) for v in run) / sum(int(v["test_count"]) for v in run) for run in by_rep.values()), "rare_class_infinite_threshold_rate": mean(int(v["threshold_is_infinite"]) for v in values if v["class_id"] == rare_class)})
    with (args.output_dir / "summary_aggregate.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(aggregate[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(aggregate)
    for metric, title, label in [("rare_class_coverage", "Rare-class coverage", "coverage"), ("mean_set_size", "Mean prediction-set size", "labels"), ("mean_ordinal_span", "Mean ordinal span", "span"), ("rare_class_infinite_threshold_rate", "Rare-class infinite-threshold rate", "rate")]:
        _write_svg(args.output_dir / f"{metric}.svg", title, label, {method: [(count, float(next(row[metric] for row in aggregate if row["rare_count"] == count and row["method"] == method))) for count in rare_counts] for method in METHODS})
    selected_rows = [row for row in aggregate if row["method"] in ("independent_mondrian", "linear_structured_final_mondrian")]
    result_table = "\n".join(
        f"| {row['rare_count']} | {row['method']} | {float(row['rare_class_coverage']):.3f} | {float(row['mean_set_size']):.3f} | {float(row['rare_class_infinite_threshold_rate']):.2f} |"
        for row in selected_rows
    )
    (args.output_dir / "interpretation.md").write_text(f"""# Minimal synthetic linear structured $q_k$ result

This is an **exploratory** hard-split proof-of-concept, not a canonical method result.

## Result

The final residual-Mondrian threshold is algebraically identical to applying independent Mondrian calibration to the final split alone, class by class:

$$\\widetilde q_{{k}} + Q^{{conf}}_{{1-\\alpha}}(S-\\widetilde q_{{k}})=Q^{{conf}}_{{1-\\alpha}}(S).$$

The saved summaries should therefore show class-conditional coverage at or above the conservative target when the final threshold is finite, but no efficiency advantage attributable to the linear preliminary fit.  Relative to independent Mondrian using the whole calibration stage, hard splitting reduces final class support and makes $+\\infty$ thresholds occur sooner.  With $\\alpha=0.10$, the exact rank is finite only for at least 9 final class observations; the prescribed half split consequently makes the rare-class final threshold uninformative for total supports 10 and 5.

| Total rare calibration support | Method | Rare-class coverage | Mean set size | Rare $+\\infty$ rate |
| ---: | --- | ---: | ---: | ---: |
{result_table}

## Recommendation

**NO-GO / revisit the hard-split construction as an efficiency method.** The final correction preserves validity, but translation equivariance eliminates any preliminary-threshold gain for an additive classwise residual correction. The next research direction, if pursued, should be a separately justified sample-efficient construction (for example cross-fitting), not extra complexity layered onto this hard split.

## Files

- `config.json`: generator, split, seed, code commit, and configuration hash.
- `per_run_results.csv`: raw method/class/repetition results and threshold diagnostics.
- `summary_by_class.csv`: requested classwise coverage, size/span, variances, corrections, and infinite rates.
- `summary_aggregate.csv`: marginal, worst-class, rare-class, and efficiency summaries.
- `*.svg`: performance versus rare-class calibration count.
""")


if __name__ == "__main__":
    main()
