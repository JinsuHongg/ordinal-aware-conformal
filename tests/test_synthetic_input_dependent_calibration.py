import unittest

from ordinal_aware_conformal.calibration.synthetic_linear import (
    fit_input_dependent_structured_mondrian,
    fit_nonordinal_input_dependent_mondrian,
)


class InputDependentSyntheticCalibrationTests(unittest.TestCase):
    def test_preliminary_threshold_varies_with_feature_within_class(self) -> None:
        features = [0.0, 1.0] * 20
        labels = [index % 5 for index in range(40)]
        scores = [0.2 + 0.5 * feature + 0.05 * label + 0.03 * feature * label for feature, label in zip(features, labels)]
        result = fit_input_dependent_structured_mondrian(features, labels, scores, features, labels, scores, 0.10, 5)
        self.assertNotEqual(result.preliminary_threshold(0.0, 2), result.preliminary_threshold(1.0, 2))

    def test_structured_fit_is_independent_of_calibration_scores(self) -> None:
        features = [0.0, 1.0] * 20
        labels = [index % 5 for index in range(40)]
        scores = [0.2 + 0.5 * feature + 0.05 * label for feature, label in zip(features, labels)]
        first = fit_input_dependent_structured_mondrian(features, labels, scores, features, labels, scores, 0.10, 5)
        second = fit_input_dependent_structured_mondrian(features, labels, scores, features, labels, [score + 3.0 for score in scores], 0.10, 5)
        self.assertEqual(first.coefficients, second.coefficients)

    def test_nonordinal_models_are_separate_by_class(self) -> None:
        features = [0.0, 1.0] * 20
        labels = [index % 5 for index in range(40)]
        scores = [0.2 + 0.5 * feature + 0.12 * label for feature, label in zip(features, labels)]
        result = fit_nonordinal_input_dependent_mondrian(features, labels, scores, features, labels, scores, 0.10, 5)
        self.assertNotEqual(result.coefficients[0], result.coefficients[4])
