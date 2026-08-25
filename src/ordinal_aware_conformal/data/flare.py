"""Solar-flare target filtering and split-assignment provenance helpers."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd


def filter_ocqr_flare_rows(
    flare_index: pd.DataFrame,
    *,
    ordinal_label_column: str = "max_goes_class",
    numeric_target_column: str = "max_intensity",
    fq_max_intensity: float | None = None,
    excluded_goes_classes: tuple[str, ...] = (),
) -> pd.DataFrame:
    """Apply the fixed raw-flux retained-population rule without mutation."""
    exclusion_masks = ocqr_flare_row_exclusion_masks(
        flare_index,
        ordinal_label_column=ordinal_label_column,
        numeric_target_column=numeric_target_column,
        fq_max_intensity=fq_max_intensity,
        excluded_goes_classes=excluded_goes_classes,
    )
    excluded = pd.Series(False, index=flare_index.index, dtype=bool)
    for mask in exclusion_masks.values():
        excluded |= mask
    return flare_index.loc[~excluded].copy()


def ocqr_flare_row_exclusion_masks(
    flare_index: pd.DataFrame,
    *,
    ordinal_label_column: str = "max_goes_class",
    numeric_target_column: str = "max_intensity",
    fq_max_intensity: float | None = None,
    excluded_goes_classes: tuple[str, ...] = (),
) -> dict[str, pd.Series]:
    """Return named non-mutating masks for the documented Solar rule."""
    required_columns = {ordinal_label_column}
    if fq_max_intensity is not None:
        required_columns.add(numeric_target_column)
    missing_columns = required_columns.difference(flare_index.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Flare index is missing required columns: {missing}.")

    labels = flare_index[ordinal_label_column].astype("string").str.strip().str.upper()
    masks: dict[str, pd.Series] = {}
    if fq_max_intensity is not None:
        numeric_target = pd.to_numeric(flare_index[numeric_target_column], errors="coerce")
        invalid_fq_target = (labels == "FQ") & ~np.isfinite(numeric_target)
        if invalid_fq_target.any():
            raise ValueError(
                "FQ rows must have finite numeric targets when applying the "
                "raw-flux retained-population rule."
            )
        masks["fq_intensity_at_or_above_threshold"] = (
            (labels == "FQ") & (numeric_target >= fq_max_intensity)
        )
    if excluded_goes_classes:
        excluded = {str(label).strip().upper() for label in excluded_goes_classes}
        masks["excluded_goes_class"] = labels.isin(excluded)
    return masks


def build_ocqr_flare_manifest_audit(
    flare_index_path: str,
    *,
    split_name: str,
    ordinal_label_column: str = "max_goes_class",
    numeric_target_column: str = "max_intensity",
    fq_max_intensity: float | None = None,
    excluded_goes_classes: tuple[str, ...] = (),
) -> dict[str, object]:
    """Record source and retained-row hashes for a frozen Solar split."""
    source_path = Path(flare_index_path)
    raw = pd.read_csv(source_path)
    masks = ocqr_flare_row_exclusion_masks(
        raw,
        ordinal_label_column=ordinal_label_column,
        numeric_target_column=numeric_target_column,
        fq_max_intensity=fq_max_intensity,
        excluded_goes_classes=excluded_goes_classes,
    )
    excluded = pd.Series(False, index=raw.index, dtype=bool)
    for mask in masks.values():
        excluded |= mask
    retained = raw.loc[~excluded].copy()
    labels = retained[ordinal_label_column].map(_map_goes_class)
    retained_csv = retained.to_csv(index=False, lineterminator="\n").encode("utf-8")
    return {
        "split": split_name,
        "source_index": {
            "path": str(source_path),
            "sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
            "row_count": int(len(raw)),
        },
        "retained_manifest": {
            "sha256": hashlib.sha256(retained_csv).hexdigest(),
            "row_count": int(len(retained)),
            "hash_representation": "UTF-8 CSV after policy filtering; source row order and columns preserved",
            "class_counts": {str(class_id): int((labels == class_id).sum()) for class_id in range(5)},
        },
        "exclusions": {
            "total": int(excluded.sum()),
            "by_reason": {reason: int(mask.sum()) for reason, mask in masks.items()},
        },
    }


def _map_goes_class(value: object) -> int:
    """Map a supplied GOES/FQ class value to the canonical ordinal index."""
    if pd.isna(value):
        raise ValueError("GOES class label must not be missing.")
    normalized_value = str(value).strip().upper()
    if normalized_value == "FQ":
        return 0
    mapping = {"A": 0, "B": 1, "C": 2, "M": 3, "X": 4}
    class_name = normalized_value[0]
    if class_name not in mapping:
        raise ValueError(f"Unknown GOES class label: {value!r}.")
    return mapping[class_name]
