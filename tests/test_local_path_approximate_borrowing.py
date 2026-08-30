import math
import unittest

from ordinal_aware_conformal.calibration.local_path_approximate_borrowing import (
    directed_path_cost, fit_local_path_approximate_borrowing, path_borrowing_cost, select_support_maximizing_radius,
)


PROBABILITIES = (0.30, 0.25, 0.22, 0.20, 0.03)
FORWARD = (0.01, 0.02, 0.30, 0.01)
BACKWARD = (0.00, 0.00, 0.00, 0.00)


class LocalPathApproximateBorrowingTests(unittest.TestCase):
    def test_zero_self_cost(self) -> None:
        self.assertEqual(directed_path_cost(3, 3, FORWARD, BACKWARD), 0.0)

    def test_path_costs_are_nonnegative(self) -> None:
        self.assertGreaterEqual(directed_path_cost(4, 1, FORWARD, BACKWARD), 0.0)

    def test_one_edge_paths_preserve_direction(self) -> None:
        self.assertEqual(directed_path_cost(2, 3, FORWARD, BACKWARD), FORWARD[2])
        self.assertEqual(directed_path_cost(3, 2, FORWARD, BACKWARD), BACKWARD[2])

    def test_multi_edge_paths_sum_in_correct_direction(self) -> None:
        self.assertEqual(directed_path_cost(1, 4, FORWARD, BACKWARD), 0.33)
        self.assertEqual(directed_path_cost(4, 1, FORWARD, BACKWARD), 0.0)

    def test_directed_triangle_inequality_on_controlled_costs(self) -> None:
        self.assertLessEqual(directed_path_cost(1, 4, FORWARD, BACKWARD), directed_path_cost(1, 2, FORWARD, BACKWARD) + directed_path_cost(2, 4, FORWARD, BACKWARD))

    def test_mixture_transfer_cost_is_nonnegative(self) -> None:
        self.assertGreaterEqual(path_borrowing_cost(PROBABILITIES, 4, 1, FORWARD, BACKWARD), 0.0)

    def test_slack_admissibility(self) -> None:
        radius, cost = select_support_maximizing_radius(PROBABILITIES, 4, FORWARD, BACKWARD, 0.01)
        self.assertLessEqual(cost, 0.01)
        self.assertEqual(radius, 1)

    def test_zero_slack_allows_zero_cost_neighbor(self) -> None:
        radius, cost = select_support_maximizing_radius(PROBABILITIES, 4, FORWARD, BACKWARD, 0.0)
        self.assertEqual(radius, 0)  # 3 -> 4 has positive forward cost in this fixture.
        self.assertEqual(cost, 0.0)

    def test_exact_rank_and_infinity_convention(self) -> None:
        result = fit_local_path_approximate_borrowing([4] * 5, [1.0] * 5, .10, 5, PROBABILITIES, FORWARD, BACKWARD, 0.0)
        self.assertIsNone(result.ranks[4])
        self.assertTrue(math.isinf(result.thresholds[4]))

    def test_reproducibility(self) -> None:
        args = ([0, 3, 4, 4], [0.1, 0.2, 0.3, 0.4], .10, 5, PROBABILITIES, FORWARD, BACKWARD, .01)
        self.assertEqual(fit_local_path_approximate_borrowing(*args), fit_local_path_approximate_borrowing(*args))
