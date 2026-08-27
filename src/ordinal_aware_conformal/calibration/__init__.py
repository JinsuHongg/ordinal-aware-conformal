"""Exploratory calibration rules used by synthetic method-development studies."""

from .synthetic_linear import (
    CalibrationResult,
    conformal_quantile,
    fit_independent_mondrian,
    fit_linear_structured_mondrian,
    fit_ordinal_cluster,
)

__all__ = [
    "CalibrationResult",
    "conformal_quantile",
    "fit_independent_mondrian",
    "fit_linear_structured_mondrian",
    "fit_ordinal_cluster",
]
