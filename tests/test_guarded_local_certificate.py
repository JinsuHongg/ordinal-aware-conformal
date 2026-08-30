import unittest

from ordinal_aware_conformal.calibration.guarded_local_certificate import (
    directional_local_ucb, reeve_uniform_upper_radius, upper_tail_interval,
)


class GuardedLocalCertificateTests(unittest.TestCase):
    def test_uniform_radius_is_bounded_and_shrinks(self) -> None:
        self.assertGreaterEqual(reeve_uniform_upper_radius(0.9, 100, 0.005), 0.0)
        self.assertLess(reeve_uniform_upper_radius(0.9, 10_000, 0.005), reeve_uniform_upper_radius(0.9, 100, 0.005))

    def test_upper_tail_interval_is_reproducible(self) -> None:
        self.assertEqual(upper_tail_interval([1.0, 2.0, 3.0, 4.0], 0.75), (3.0, float("inf")))

    def test_directional_ucb_is_bounded_and_oriented(self) -> None:
        source, target = [0.0] * 40, [1.0] * 40
        empirical, ucb = directional_local_ucb(source, target, (0.0, float("inf")), 0.005)
        self.assertEqual(empirical, 1.0)
        self.assertEqual(ucb, 1.0)

    def test_unsupported_score_group_is_safe(self) -> None:
        self.assertEqual(directional_local_ucb([], [1.0], (0.0, float("inf")), 0.005), (1.0, 1.0))
