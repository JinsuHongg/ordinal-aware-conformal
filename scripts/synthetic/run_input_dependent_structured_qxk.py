#!/usr/bin/env python3
"""Evaluate a frozen input-dependent ordinal threshold with full Mondrian residuals."""
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

from ordinal_aware_conformal.calibration.synthetic_linear import (
    InputDependentCalibrationResult,
    fit_independent_mondrian,
    fit_input_dependent_structured_mondrian,
)


METHODS = ("independent_mondrian", "input_dependent_structured_mondrian")


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _draw_label(rng: random.Random, probabilities: list[float]) -> int:
    draw, cumulative = rng.random(), 0.0
    for label, probability in enumerate(probabilities):
        cumulative += probability
        if draw < cumulative:
            return label
    return len(probabilities) - 1


def _sigma(feature: float, label: int) -> float:
    """Smooth ordinal heteroscedasticity; feature predicts within-class difficulty."""
    return 0.09 + 0.38 * feature + 0.035 * label + 0.018 * feature * label


def _sample_true_scores(rng: random.Random, features: list[float], labels: list[int]) -> list[float]:
    return [abs(rng.gauss(0.0, _sigma(feature, label))) for feature, label in zip(features, labels, strict=True)]


def _sample_candidate_scores(rng: random.Random, features: list[float], labels: list[int], n_classes: int, embedding_step: float) -> list[list[float]]:
    rows = []
    for feature, label in zip(features, labels, strict=True):
        prediction = embedding_step * label + rng.gauss(0.0, _sigma(feature, label))
        rows.append([abs(prediction - embedding_step * candidate) for candidate in range(n_classes)])
    return rows


def _metrics(features: list[float], labels: list[int], candidate_scores: list[list[float]], result: object, n_classes: int) -> dict[int, dict[str, float]]:
    grouped: dict[int, list[tuple[bool, int, int, float, float]]] = defaultdict(list)
    for feature, label, scores in zip(features, labels, candidate_scores, strict=True):
        if isinstance(result, InputDependentCalibrationResult):
            thresholds = [result.final_threshold(feature, candidate) for candidate in range(n_classes)]
            preliminary = result.preliminary_threshold(feature, label)
            correction = result.corrections[label]
        else:
            thresholds = list(result.thresholds)  # type: ignore[attr-defined]
            preliminary, correction = 0.0, result.thresholds[label]  # type: ignore[attr-defined]
        prediction_set = [candidate for candidate, score in enumerate(scores) if score <= thresholds[candidate]]
        span = prediction_set[-1] - prediction_set[0] + 1 if prediction_set else 0
        grouped[label].append((label in prediction_set, len(prediction_set), span, preliminary, correction))
    return {label: {"coverage": mean(item[0] for item in values), "mean_set_size": mean(item[1] for item in values), "mean_ordinal_span": mean(item[2] for item in values), "mean_preliminary_threshold": mean(item[3] for item in values), "preliminary_threshold_variance": pvariance(item[3] for item in values), "mean_correction": mean(item[4] for item in values)} for label, values in grouped.items()}


def _write_svg(path: Path, title: str, y_label: str, series: dict[str, list[tuple[int, float]]]) -> None:
    width, height, left, bottom = 760, 460, 85, 65
    points = [point for values in series.values() for point in values]
    xs, ys = [point[0] for point in points], [point[1] for point in points]
    x_min, x_max, y_min, y_max = min(xs), max(xs), min(0.0, min(ys)), max(ys)
    if y_min == y_max: y_max += 1.0
    def x(value: float) -> float: return left + (width - left - 35) * (value - x_min) / max(1, x_max - x_min)
    def y(value: float) -> float: return height - bottom - (height - bottom - 55) * (value - y_min) / (y_max - y_min)
    colors = {"independent_mondrian": "#1f77b4", "input_dependent_structured_mondrian": "#2ca02c"}
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><rect width="100%" height="100%" fill="white"/><text x="{left}" y="28" font-size="18" font-family="sans-serif">{title}</text><line x1="{left}" y1="55" x2="{left}" y2="{height-bottom}" stroke="black"/><line x1="{left}" y1="{height-bottom}" x2="{width-35}" y2="{height-bottom}" stroke="black"/>']
    for value in sorted(set(xs)): parts.append(f'<text x="{x(value)-8:.1f}" y="{height-bottom+20}" font-size="11" font-family="sans-serif">{value}</text>')
    parts.append(f'<text x="{width/2-85}" y="{height-12}" font-size="13" font-family="sans-serif">rare-class calibration count</text><text x="18" y="{height/2}" transform="rotate(-90 18 {height/2})" font-size="13" font-family="sans-serif">{y_label}</text>')
    for index, (method, values) in enumerate(series.items()):
        ordered, color = sorted(values), colors[method]
        parts.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.5" points="{" ".join(f"{x(a):.1f},{y(b):.1f}" for a,b in ordered)}"/>')
        parts.extend(f'<circle cx="{x(a):.1f}" cy="{y(b):.1f}" r="3.5" fill="{color}"/>' for a, b in ordered)
        parts.append(f'<text x="{width-310}" y="{55+22*index}" font-size="12" font-family="sans-serif" fill="{color}">{method}</text>')
    path.write_text("\n".join(parts + ["</svg>"]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/synthetic_input_dependent_structured_qxk"))
    parser.add_argument("--repetitions", type=int, default=50)
    parser.add_argument("--test-size", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20260828)
    args = parser.parse_args()
    n_classes, alpha, rare_class, rare_counts = 5, 0.10, 0, [100, 50, 20, 10, 5]
    probabilities = [0.05, 0.2375, 0.2375, 0.2375, 0.2375]
    embedding_step = 0.60
    config = {"study": "exploratory_synthetic_input_dependent_structured_qxk", "method_version": "exploratory-frozen-input-dependent-v1", "n_classes": n_classes, "alpha": alpha, "rare_class": rare_class, "rare_counts": rare_counts, "other_class_calibration_count": 100, "structured_training_size": 4000, "class_probabilities": probabilities, "ordinal_embedding_step": embedding_step, "score": "S(x,k)=|z-0.60*k|; z=0.60*Y+Normal(0,sigma(x,Y))", "sigma": "0.09+0.38*x+0.035*k+0.018*x*k", "preliminary_model": "Gaussian-quantile-scaled least-squares [1,x,k,x*k] fit on independent structured-training data", "calibration": "full class-specific residual Mondrian; no calibration observations used to fit preliminary model", "repetitions": args.repetitions, "test_size": args.test_size, "seed": args.seed}
    config["config_hash"] = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest(); config["code_commit"] = _git_commit()
    args.output_dir.mkdir(parents=True, exist_ok=True); (args.output_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    rows: list[dict[str, object]] = []
    for rare_count in rare_counts:
        for repetition in range(args.repetitions):
            rng = random.Random(args.seed + rare_count * 10_000 + repetition)
            train_features = [rng.random() for _ in range(config["structured_training_size"])]
            train_labels = [_draw_label(rng, probabilities) for _ in train_features]
            train_scores = _sample_true_scores(rng, train_features, train_labels)
            calibration_labels = [label for label in range(n_classes) for _ in range(rare_count if label == rare_class else 100)]
            calibration_features = [rng.random() for _ in calibration_labels]
            calibration_scores = _sample_true_scores(rng, calibration_features, calibration_labels)
            results = {"independent_mondrian": fit_independent_mondrian(calibration_labels, calibration_scores, alpha, n_classes), "input_dependent_structured_mondrian": fit_input_dependent_structured_mondrian(train_features, train_labels, train_scores, calibration_features, calibration_labels, calibration_scores, alpha, n_classes)}
            test_features = [rng.random() for _ in range(args.test_size)]
            test_labels = [_draw_label(rng, probabilities) for _ in test_features]
            candidate_scores = _sample_candidate_scores(rng, test_features, test_labels, n_classes, embedding_step)
            for method, result in results.items():
                for label, values in _metrics(test_features, test_labels, candidate_scores, result, n_classes).items():
                    correction_or_threshold = result.corrections[label] if isinstance(result, InputDependentCalibrationResult) else result.thresholds[label]
                    rows.append({"rare_count": rare_count, "repetition": repetition, "method": method, "class_id": label, "test_count": sum(test_label == label for test_label in test_labels), **values, "correction_is_infinite": int(isinf(correction_or_threshold)), "calibration_support": result.final_support[label] if isinstance(result, InputDependentCalibrationResult) else calibration_labels.count(label)})
    with (args.output_dir / "per_run_results.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    grouped: dict[tuple[int, str, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows: grouped[(int(row["rare_count"]), str(row["method"]), int(row["class_id"]))].append(row)
    summary = [{"rare_count": count, "method": method, "class_id": label, "mean_coverage": mean(float(v["coverage"]) for v in values), "mean_set_size": mean(float(v["mean_set_size"]) for v in values), "mean_ordinal_span": mean(float(v["mean_ordinal_span"]) for v in values), "mean_preliminary_threshold": mean(float(v["mean_preliminary_threshold"]) for v in values), "mean_preliminary_threshold_variance": mean(float(v["preliminary_threshold_variance"]) for v in values), "mean_correction": mean(float(v["mean_correction"]) for v in values), "correction_infinite_rate": mean(int(v["correction_is_infinite"]) for v in values), "calibration_support": values[0]["calibration_support"]} for (count, method, label), values in sorted(grouped.items())]
    with (args.output_dir / "summary_by_class.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0]), lineterminator="\n"); writer.writeheader(); writer.writerows(summary)
    aggregate = []
    for count in rare_counts:
        for method in METHODS:
            values = [row for row in rows if row["rare_count"] == count and row["method"] == method]
            runs: dict[int, list[dict[str, object]]] = defaultdict(list)
            for value in values: runs[int(value["repetition"])].append(value)
            aggregate.append({"rare_count": count, "method": method, "marginal_coverage": mean(sum(float(v["coverage"])*int(v["test_count"]) for v in run)/sum(int(v["test_count"]) for v in run) for run in runs.values()), "worst_class_coverage": mean(min(float(v["coverage"]) for v in run) for run in runs.values()), "rare_class_coverage": mean(float(v["coverage"]) for v in values if v["class_id"] == rare_class), "mean_set_size": mean(sum(float(v["mean_set_size"])*int(v["test_count"]) for v in run)/sum(int(v["test_count"]) for v in run) for run in runs.values()), "mean_ordinal_span": mean(sum(float(v["mean_ordinal_span"])*int(v["test_count"]) for v in run)/sum(int(v["test_count"]) for v in run) for run in runs.values()), "rare_correction_infinite_rate": mean(int(v["correction_is_infinite"]) for v in values if v["class_id"] == rare_class)})
    with (args.output_dir / "summary_aggregate.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(aggregate[0]), lineterminator="\n"); writer.writeheader(); writer.writerows(aggregate)
    for metric, title, label in [("rare_class_coverage", "Rare-class coverage", "coverage"), ("mean_set_size", "Mean prediction-set size", "labels"), ("mean_ordinal_span", "Mean ordinal span", "span")]: _write_svg(args.output_dir / f"{metric}.svg", title, label, {method: [(count, float(next(row[metric] for row in aggregate if row["rare_count"] == count and row["method"] == method))) for count in rare_counts] for method in METHODS})
    table = "\n".join(f"| {row['rare_count']} | {row['method']} | {float(row['rare_class_coverage']):.3f} | {float(row['mean_set_size']):.3f} |" for row in aggregate)
    (args.output_dir / "interpretation.md").write_text(f"""# Input-dependent structured threshold: synthetic result

This is an **exploratory** study, not a canonical method or theorem claim.

The preliminary threshold is trained and frozen using an independent sample, then the full calibration set supplies class-specific residual-Mondrian corrections. Conditional on this frozen function, the residual is a fixed transformed score; the intended validity route is the standard within-class Mondrian rank argument.

| Rare calibration support | Method | Rare-class coverage | Mean set size |
| ---: | --- | ---: | ---: |
{table}

Interpret these results together with `summary_by_class.csv`: the input-dependent method is useful only if it retains approximately 0.90 classwise coverage while reducing set size/span or residual correction magnitude without discarding calibration support. The experiment does not tune any model setting on test outcomes.

## First controlled interpretation

In this favorable, correctly structured heteroscedastic regime, finite-support settings provide a **GO signal for further validation** when the table shows target-level rare-class coverage with a smaller mean set size. This is not sufficient to freeze a method: the preliminary model matches the generator's affine ordinal difficulty pattern, so the next test should assess misspecification and weaker ordinal smoothness without changing the final residual-Mondrian rule. At rare support five, the exact finite-rank convention makes both methods uninformative; this construction preserves full calibration support but cannot overcome that fundamental limit.
""")


if __name__ == "__main__":
    main()
