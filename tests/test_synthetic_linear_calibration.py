from math import inf
import unittest
from ordinal_aware_conformal.calibration.synthetic_linear import (
    conformal_quantile,
    fit_independent_mondrian,
    fit_linear_structured_mondrian,
)


class SyntheticLinearCalibrationTests(unittest.TestCase):
    def test_conformal_quantile_uses_conservative_infinity_for_insufficient_support(self) -> None:
        self.assertEqual(conformal_quantile([1.0] * 8, 0.10), inf)
        self.assertEqual(conformal_quantile(list(range(9)), 0.10), 8)


    def test_final_residual_threshold_is_translation_equivariant_within_class(self) -> None:
        structured_labels = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]
        structured_scores = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        final_labels = [0] * 10 + [1] * 10 + [2] * 10 + [3] * 10 + [4] * 10
        final_scores = [0.01 * index + label for label in range(5) for index in range(10)]
        structured = fit_linear_structured_mondrian(structured_labels, structured_scores, final_labels, final_scores, 0.10, 5)
        final_only = fit_independent_mondrian(final_labels, final_scores, 0.10, 5)
        self.assertEqual(structured.thresholds, final_only.thresholds)
