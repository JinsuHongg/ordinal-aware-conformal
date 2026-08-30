import math
import unittest

from ordinal_aware_conformal.calibration.generic_directional_borrowing import (
    direct_directional_cost, fit_generic_directional_borrowing, is_contiguous, select_generic_group, subsets_containing_target,
)
from ordinal_aware_conformal.synthetic.ordinal_borrowing_generator import normal_ks


PROBABILITIES = (0.30, 0.25, 0.22, 0.20, 0.03)
DIRECTIONAL = (
    (0.0, 0.01, 0.02, 0.03, 0.0),
    (0.0, 0.0, 0.01, 0.02, 0.0),
    (0.0, 0.0, 0.0, 0.01, 0.0),
    (0.0, 0.0, 0.0, 0.0, 0.02),
    (0.0, 0.0, 0.0, 0.0, 0.0),
)


class GenericDirectionalBorrowingTests(unittest.TestCase):
    def test_direct_directional_transfer_on_normal_distributions(self) -> None:
        probabilities, group, target = (0.20, 0.03), (0, 1), 1
        discrepancy = normal_ks(0.515, 0.520, 0.20)
        matrix = ((0.0, discrepancy), (0.0, 0.0))
        cost = direct_directional_cost(probabilities, target, group, matrix)
        weight = probabilities[0] / sum(probabilities)
        for index in range(1001):
            value = -1.0 + 3.0 * index / 1000
            first = .5 * (1.0 + math.erf((value - .515) / (math.sqrt(2.0) * .20)))
            second = .5 * (1.0 + math.erf((value - .520) / (math.sqrt(2.0) * .20)))
            self.assertLessEqual(weight * (first - second), cost + 1e-12)

    def test_target_only_group_has_zero_cost(self) -> None:
        self.assertEqual(direct_directional_cost(PROBABILITIES, 4, (4,), DIRECTIONAL), 0.0)

    def test_all_subsets_are_enumerated_once(self) -> None:
        groups = subsets_containing_target(5, 4)
        self.assertEqual(len(groups), 16)
        self.assertEqual(len(set(groups)), 16)
        self.assertTrue(all(4 in group for group in groups))

    def test_selected_group_satisfies_slack_and_is_support_optimal(self) -> None:
        group, cost = select_generic_group(PROBABILITIES, 4, DIRECTIONAL, 0.0)
        self.assertLessEqual(cost, 0.0)
        self.assertEqual(group, (0, 1, 2, 4))

    def test_tie_breaking_is_deterministic(self) -> None:
        self.assertEqual(select_generic_group(PROBABILITIES, 4, DIRECTIONAL, 0.01), select_generic_group(PROBABILITIES, 4, DIRECTIONAL, 0.01))

    def test_contiguity_detection(self) -> None:
        self.assertTrue(is_contiguous((1, 2, 3)))
        self.assertFalse(is_contiguous((0, 2, 3)))

    def test_exact_rank_and_reproducibility(self) -> None:
        result = fit_generic_directional_borrowing([4] * 5, [1.0] * 5, .10, 5, PROBABILITIES, DIRECTIONAL, 0.0)
        self.assertTrue(math.isinf(result.thresholds[4]))
        self.assertEqual(result, fit_generic_directional_borrowing([4] * 5, [1.0] * 5, .10, 5, PROBABILITIES, DIRECTIONAL, 0.0))
