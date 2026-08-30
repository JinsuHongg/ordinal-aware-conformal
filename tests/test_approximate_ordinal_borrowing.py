import math
import unittest

from ordinal_aware_conformal.calibration.approximate_ordinal_borrowing import (
    borrowing_cost, fit_approximate_ordinal_borrowing, select_largest_admissible_radius,
)
from ordinal_aware_conformal.synthetic.ordinal_borrowing_generator import SCENARIOS, normal_ks


PROBABILITIES = (0.30, 0.25, 0.22, 0.20, 0.03)


class ApproximateOrdinalBorrowingTests(unittest.TestCase):
    def test_zero_radius_has_zero_cost(self) -> None:
        self.assertEqual(borrowing_cost(PROBABILITIES, 4, 0, 0.1), 0.0)

    def test_cost_is_nonnegative(self) -> None:
        self.assertGreaterEqual(borrowing_cost(PROBABILITIES, 4, 1, 0.1), 0.0)

    def test_strong_smoothness_transfer_is_bounded(self) -> None:
        scenario = SCENARIOS["strong_smoothness"]
        lipschitz = normal_ks(0.500, 0.505, scenario.sigma)
        cost = borrowing_cost(PROBABILITIES, 4, 1, lipschitz)
        weight = PROBABILITIES[3] / (PROBABILITIES[3] + PROBABILITIES[4])
        for index in range(1001):
            value = -1.0 + 3.0 * index / 1000
            cdf3 = 0.5 * (1.0 + math.erf((value - 0.515) / (math.sqrt(2.0) * scenario.sigma)))
            cdf4 = 0.5 * (1.0 + math.erf((value - 0.520) / (math.sqrt(2.0) * scenario.sigma)))
            self.assertLessEqual(weight * (cdf3 - cdf4), cost + 1e-12)

    def test_selected_radius_obeys_slack(self) -> None:
        radius, cost = select_largest_admissible_radius(PROBABILITIES, 4, 0.1, 0.09)
        self.assertLessEqual(cost, 0.09)
        self.assertGreaterEqual(radius, 0)

    def test_larger_slack_cannot_reduce_radius(self) -> None:
        low, _ = select_largest_admissible_radius(PROBABILITIES, 4, 0.1, 0.01)
        high, _ = select_largest_admissible_radius(PROBABILITIES, 4, 0.1, 0.10)
        self.assertGreaterEqual(high, low)

    def test_exact_conformal_rank_and_infinity_convention(self) -> None:
        result = fit_approximate_ordinal_borrowing([4] * 5, [1.0] * 5, 0.10, 5, PROBABILITIES, 0.0, 0.0)
        self.assertIsNone(result.ranks[4])
        self.assertTrue(math.isinf(result.thresholds[4]))

    def test_iid_input_is_not_required_to_have_fixed_counts(self) -> None:
        labels = [0, 0, 1, 3, 4]
        result = fit_approximate_ordinal_borrowing(labels, [0.1] * len(labels), 0.10, 5, PROBABILITIES, 0.01, 0.01)
        self.assertEqual(result.own_support, (2, 1, 0, 1, 1))

    def test_same_inputs_are_reproducible(self) -> None:
        args = ([0, 3, 4, 4], [0.1, 0.2, 0.3, 0.4], 0.10, 5, PROBABILITIES, 0.01, 0.01)
        self.assertEqual(fit_approximate_ordinal_borrowing(*args), fit_approximate_ordinal_borrowing(*args))
