#!/usr/bin/env python3
"""Robustness study for frozen input-dependent ordinal residual calibration.

Each scenario uses independent structured-training data, then the entire
class-labelled calibration set for the unchanged exact Mondrian residual rule.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from collections import defaultdict
from math import isinf, sin
from pathlib import Path
from statistics import mean, pstdev

from ordinal_aware_conformal.calibration.synthetic_linear import (
    InputDependentCalibrationResult, NonOrdinalInputDependentCalibrationResult,
    fit_independent_mondrian, fit_input_dependent_structured_mondrian,
    fit_nonordinal_input_dependent_mondrian, fit_ordinal_cluster,
)


METHODS = ("independent_mondrian", "ordinal_cluster", "input_dependent_nonordinal", "input_dependent_ordinal")
SCENARIOS = ("A_well_specified", "B_nonlinear_misspecified", "C_weaker_ordinal_smoothness", "D_no_useful_ordinal_structure")
OFFSETS = {
    "C_weaker_ordinal_smoothness": (0.12, 0.16, 0.30, 0.19, 0.26),
    "D_no_useful_ordinal_structure": (0.27, 0.10, 0.33, 0.14, 0.25),
}


def sigma(scenario: str, feature: float, label: int) -> float:
    if scenario == "A_well_specified":
        return 0.09 + 0.38 * feature + 0.035 * label + 0.018 * feature * label
    if scenario == "B_nonlinear_misspecified":
        return 0.11 + 0.30 * feature * feature + 0.025 * label + 0.065 * abs(sin(1.7 * label)) + 0.012 * feature * feature * label
    if scenario == "C_weaker_ordinal_smoothness":
        return OFFSETS[scenario][label] + 0.30 * feature + 0.010 * feature * label
    return OFFSETS[scenario][label] + 0.30 * feature


def draw_label(rng: random.Random, probabilities: list[float]) -> int:
    draw = rng.random(); total = 0.0
    for label, probability in enumerate(probabilities):
        total += probability
        if draw < total: return label
    return len(probabilities) - 1


def true_scores(rng: random.Random, scenario: str, features: list[float], labels: list[int]) -> list[float]:
    return [abs(rng.gauss(0.0, sigma(scenario, feature, label))) for feature, label in zip(features, labels, strict=True)]


def candidate_scores(rng: random.Random, scenario: str, features: list[float], labels: list[int], n_classes: int, step: float) -> list[list[float]]:
    rows = []
    for feature, label in zip(features, labels, strict=True):
        prediction = step * label + rng.gauss(0.0, sigma(scenario, feature, label))
        rows.append([abs(prediction - step * candidate) for candidate in range(n_classes)])
    return rows


def thresholds(result: object, feature: float, n_classes: int) -> list[float]:
    if isinstance(result, (InputDependentCalibrationResult, NonOrdinalInputDependentCalibrationResult)):
        return [result.final_threshold(feature, label) for label in range(n_classes)]
    return list(result.thresholds)  # type: ignore[attr-defined]


def diagnostics(result: object, feature: float, label: int) -> tuple[float, float]:
    if isinstance(result, (InputDependentCalibrationResult, NonOrdinalInputDependentCalibrationResult)):
        return result.preliminary_threshold(feature, label), result.corrections[label]
    return 0.0, result.thresholds[label]  # type: ignore[attr-defined]


def evaluate(features: list[float], labels: list[int], scores: list[list[float]], result: object, n_classes: int) -> dict[int, dict[str, float]]:
    grouped: dict[int, list[tuple[bool, int, int, bool, float, float, float]]] = defaultdict(list)
    for feature, label, row in zip(features, labels, scores, strict=True):
        threshold = thresholds(result, feature, n_classes)
        prediction_set = [candidate for candidate, score in enumerate(row) if score <= threshold[candidate]]
        preliminary, correction = diagnostics(result, feature, label)
        span = prediction_set[-1] - prediction_set[0] + 1 if prediction_set else 0
        grouped[label].append((label in prediction_set, len(prediction_set), span, len(prediction_set) == n_classes, preliminary, correction, threshold[label]))
    out = {}
    for label, values in grouped.items():
        finite_corrections = [value[5] for value in values if not isinf(value[5])]
        finite_final = [value[6] for value in values if not isinf(value[6])]
        out[label] = {"coverage": mean(value[0] for value in values), "mean_set_size": mean(value[1] for value in values), "mean_ordinal_span": mean(value[2] for value in values), "full_set_rate": mean(value[3] for value in values), "mean_preliminary_threshold": mean(value[4] for value in values), "preliminary_threshold_variance": pstdev(value[4] for value in values) ** 2, "mean_correction": mean(finite_corrections) if finite_corrections else float("inf"), "final_threshold_variance": pstdev(finite_final) ** 2 if finite_final else float("inf")}
    return out


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n"); writer.writeheader(); writer.writerows(rows)


def safe_sd(values: list[float]) -> float:
    return float("inf") if any(isinf(value) for value in values) else pstdev(values)


def run_scenario(scenario: str, root: Path, repetitions: int, test_size: int, seed: int) -> None:
    n_classes, alpha, rare_class, step = 5, 0.10, 0, 0.60
    rare_counts, probabilities, train_size = [100, 50, 20, 10, 5], [0.05, 0.2375, 0.2375, 0.2375, 0.2375], 4000
    output = root / scenario; output.mkdir(parents=True, exist_ok=True)
    config = {"study": "exploratory_input_dependent_robustness", "scenario": scenario, "alpha": alpha, "n_classes": n_classes, "rare_counts": rare_counts, "other_class_calibration_count": 100, "structured_training_size": train_size, "test_size": test_size, "repetitions": repetitions, "seed": seed, "ordinal_embedding_step": step, "ordinal_model": "4 parameters [1,x,k,x*k]", "nonordinal_model": "10 parameters: separate [1,x] per class", "calibration": "full class-specific exact residual Mondrian; preliminary fits use independent structured-training data only"}
    config["config_hash"] = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest(); (output / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    rows: list[dict[str, object]] = []
    for rare_count in rare_counts:
        for repetition in range(repetitions):
            rng = random.Random(seed + 1_000_000 * SCENARIOS.index(scenario) + 10_000 * rare_count + repetition)
            train_features = [rng.random() for _ in range(train_size)]; train_labels = [draw_label(rng, probabilities) for _ in train_features]
            train_scores = true_scores(rng, scenario, train_features, train_labels)
            calibration_labels = [label for label in range(n_classes) for _ in range(rare_count if label == rare_class else 100)]
            calibration_features = [rng.random() for _ in calibration_labels]; calibration_scores = true_scores(rng, scenario, calibration_features, calibration_labels)
            results = {"independent_mondrian": fit_independent_mondrian(calibration_labels, calibration_scores, alpha, n_classes), "ordinal_cluster": fit_ordinal_cluster(calibration_labels, calibration_scores, alpha, n_classes), "input_dependent_nonordinal": fit_nonordinal_input_dependent_mondrian(train_features, train_labels, train_scores, calibration_features, calibration_labels, calibration_scores, alpha, n_classes), "input_dependent_ordinal": fit_input_dependent_structured_mondrian(train_features, train_labels, train_scores, calibration_features, calibration_labels, calibration_scores, alpha, n_classes)}
            test_features = [rng.random() for _ in range(test_size)]; test_labels = [draw_label(rng, probabilities) for _ in test_features]; scores = candidate_scores(rng, scenario, test_features, test_labels, n_classes, step)
            counts = [test_labels.count(label) for label in range(n_classes)]
            for method, result in results.items():
                for label, metric in evaluate(test_features, test_labels, scores, result, n_classes).items():
                    correction = diagnostics(result, 0.5, label)[1]
                    rows.append({"scenario": scenario, "rare_count": rare_count, "repetition": repetition, "method": method, "class_id": label, "test_count": counts[label], **metric, "correction_is_infinite": int(isinf(correction)), "calibration_support": calibration_labels.count(label)})
    write_csv(output / "per_run_results.csv", rows)
    summarize(rows, output)


def summarize(rows: list[dict[str, object]], output: Path) -> None:
    by_key: dict[tuple[int, str, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows: by_key[(int(row["rare_count"]), str(row["method"]), int(row["class_id"]))].append(row)
    class_rows = []
    for (count, method, label), values in sorted(by_key.items()):
        corrections = [float(v["mean_correction"]) for v in values]
        class_rows.append({"rare_count": count, "method": method, "class_id": label, "mean_coverage": mean(float(v["coverage"]) for v in values), "coverage_sd": pstdev(float(v["coverage"]) for v in values), "mean_set_size": mean(float(v["mean_set_size"]) for v in values), "set_size_sd": pstdev(float(v["mean_set_size"]) for v in values), "mean_ordinal_span": mean(float(v["mean_ordinal_span"]) for v in values), "full_set_rate": mean(float(v["full_set_rate"]) for v in values), "mean_preliminary_threshold": mean(float(v["mean_preliminary_threshold"]) for v in values), "preliminary_threshold_variance": mean(float(v["preliminary_threshold_variance"]) for v in values), "mean_correction": mean(corrections), "correction_sd": safe_sd(corrections), "final_threshold_variance": mean(float(v["final_threshold_variance"]) for v in values), "infinite_correction_rate": mean(int(v["correction_is_infinite"]) for v in values), "calibration_support": values[0]["calibration_support"]})
    write_csv(output / "summary_by_class.csv", class_rows)
    aggregate = []
    for count in [100, 50, 20, 10, 5]:
        for method in METHODS:
            values = [row for row in rows if row["rare_count"] == count and row["method"] == method]
            runs: dict[int, list[dict[str, object]]] = defaultdict(list)
            for value in values: runs[int(value["repetition"])].append(value)
            coverage = [sum(float(v["coverage"]) * int(v["test_count"]) for v in run) / sum(int(v["test_count"]) for v in run) for run in runs.values()]
            size = [sum(float(v["mean_set_size"]) * int(v["test_count"]) for v in run) / sum(int(v["test_count"]) for v in run) for run in runs.values()]
            aggregate.append({"rare_count": count, "method": method, "marginal_coverage": mean(coverage), "marginal_coverage_sd": pstdev(coverage), "worst_class_coverage": mean(min(float(v["coverage"]) for v in run) for run in runs.values()), "rare_class_coverage": mean(float(v["coverage"]) for v in values if v["class_id"] == 0), "mean_set_size": mean(size), "mean_set_size_sd": pstdev(size), "mean_ordinal_span": mean(sum(float(v["mean_ordinal_span"]) * int(v["test_count"]) for v in run) / sum(int(v["test_count"]) for v in run) for run in runs.values()), "rare_infinite_rate": mean(int(v["correction_is_infinite"]) for v in values if v["class_id"] == 0)})
    baseline = {(row["rare_count"]): row["mean_set_size"] for row in aggregate if row["method"] == "independent_mondrian"}
    for row in aggregate: row["relative_size_vs_mondrian_pct"] = 100 * (row["mean_set_size"] - baseline[row["rare_count"]]) / baseline[row["rare_count"]]
    nonordinal = {(row["rare_count"]): row["mean_set_size"] for row in aggregate if row["method"] == "input_dependent_nonordinal"}
    for row in aggregate: row["ordinal_vs_nonordinal_size_delta"] = row["mean_set_size"] - nonordinal[row["rare_count"]]
    write_csv(output / "summary_aggregate.csv", aggregate)


def aggregate_outputs(root: Path) -> None:
    rows = []
    for scenario in SCENARIOS:
        with (root / scenario / "summary_aggregate.csv").open() as handle:
            rows.extend({"scenario": scenario, **row} for row in csv.DictReader(handle))
    write_csv(root / "scenario_method_summary.csv", rows)
    for scenario in SCENARIOS:
        current = [row for row in rows if row["scenario"] == scenario]
        plot(root / f"{scenario}_coverage.svg", "Rare-class coverage", "coverage", {method: [(int(row["rare_count"]), float(row["rare_class_coverage"])) for row in current if row["method"] == method] for method in METHODS})
        plot(root / f"{scenario}_set_size.svg", "Mean prediction-set size", "size", {method: [(int(row["rare_count"]), float(row["mean_set_size"])) for row in current if row["method"] == method] for method in METHODS})
        plot(root / f"{scenario}_relative_efficiency.svg", "Relative set-size change vs Mondrian", "percent", {method: [(int(row["rare_count"]), float(row["relative_size_vs_mondrian_pct"])) for row in current if row["method"] == method] for method in METHODS if method != "independent_mondrian"})
    plot(root / "ordinal_vs_nonordinal_ablation.svg", "Ordinal minus non-ordinal set size", "size difference", {scenario: [(int(row["rare_count"]), float(row["ordinal_vs_nonordinal_size_delta"])) for row in rows if row["scenario"] == scenario and row["method"] == "input_dependent_ordinal"] for scenario in SCENARIOS})
    table = "\n".join(f"| {row['scenario']} | {row['rare_count']} | {row['method']} | {float(row['rare_class_coverage']):.3f} | {float(row['mean_set_size']):.3f} | {float(row['relative_size_vs_mondrian_pct']):.1f}% | {float(row['ordinal_vs_nonordinal_size_delta']):.3f} |" for row in rows)
    (root / "interpretation.md").write_text(f"""# Robustness validation: frozen input-dependent ordinal calibration

This is an exploratory robustness study, not a canonical method or theorem claim. The preliminary ordinal and non-ordinal models are fit only on independent structured-training data; every residual method uses the unchanged full class-specific exact Mondrian correction.

Read `scenario_method_summary.csv` for scenario-level coverage, set size, relative efficiency versus independent Mondrian, and ordinal-versus-non-ordinal size differences. `summary_by_class.csv` within each scenario contains per-class diagnostics, including correction dispersion and infinite rates.

| Scenario | Rare support | Method | Rare coverage | Mean set size | Size vs Mondrian | Ordinal - non-ordinal |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
{table}

Interpret ordinal gains cautiously: the non-ordinal ablation has 10 parameters (two per class), while the ordinal affine model has four shared parameters. This capacity imbalance favors the non-ordinal ablation. A result where the ordinal method is no better than the ablation means the current gain is attributable primarily to input-dependent calibration rather than ordinal sharing.

The exact finite-rank rule makes both residual methods uninformative at rare support five; this is a finite-sample conformal limitation, not evidence for or against ordinal structure.
""")


def plot(path: Path, title: str, y_label: str, series: dict[str, list[tuple[int, float]]]) -> None:
    width, height, left, bottom = 820, 460, 80, 65
    points = [point for values in series.values() for point in values if not isinf(point[1])]
    x_values, y_values = [point[0] for point in points], [point[1] for point in points]
    x_min, x_max, y_min, y_max = min(x_values), max(x_values), min(0.0, min(y_values)), max(y_values)
    if y_max == y_min: y_max += 1.0
    def x(value: float) -> float: return left + (width-left-40) * (value-x_min) / max(1, x_max-x_min)
    def y(value: float) -> float: return height-bottom - (height-bottom-55) * (value-y_min) / (y_max-y_min)
    colors = ("#1f77b4", "#ff7f0e", "#2ca02c", "#d62728")
    content = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><rect width="100%" height="100%" fill="white"/><text x="{left}" y="28" font-size="18">{title}</text><line x1="{left}" y1="55" x2="{left}" y2="{height-bottom}" stroke="black"/><line x1="{left}" y1="{height-bottom}" x2="{width-40}" y2="{height-bottom}" stroke="black"/>']
    for value in sorted(set(x_values)): content.append(f'<text x="{x(value)-8:.1f}" y="{height-bottom+20}" font-size="11">{value}</text>')
    content.append(f'<text x="{width/2-90}" y="{height-12}" font-size="13">rare calibration support</text><text x="18" y="{height/2}" transform="rotate(-90 18 {height/2})" font-size="13">{y_label}</text>')
    for index, (name, values) in enumerate(series.items()):
        values, color = sorted(values), colors[index % len(colors)]
        coords = " ".join(f"{x(a):.1f},{y(b):.1f}" for a, b in values)
        content.append(f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{coords}"/><text x="{width-330}" y="{54+19*index}" font-size="11" fill="{color}">{name}</text>')
    path.write_text("\n".join(content + ["</svg>"]))


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--output-dir", type=Path, default=Path("outputs/synthetic_input_dependent_robustness")); parser.add_argument("--scenario", choices=("all", *SCENARIOS), default="all"); parser.add_argument("--aggregate-only", action="store_true"); parser.add_argument("--repetitions", type=int, default=50); parser.add_argument("--test-size", type=int, default=5000); parser.add_argument("--seed", type=int, default=20260829)
    args = parser.parse_args()
    if args.aggregate_only: aggregate_outputs(args.output_dir); return
    for scenario in (SCENARIOS if args.scenario == "all" else (args.scenario,)): run_scenario(scenario, args.output_dir, args.repetitions, args.test_size, args.seed)
    if args.scenario == "all": aggregate_outputs(args.output_dir)


if __name__ == "__main__": main()
