import unittest

from ordinal_aware_conformal.calibration.two_sample_ks_certificate import (
    two_sample_ks_radius,
    two_sample_structural_certificates,
)


class TwoSampleKSCertificateTests(unittest.TestCase):
    def test_radius_is_nonnegative_and_shrinks(self) -> None:
        small = two_sample_ks_radius(20, 30, 0.005)
        large = two_sample_ks_radius(2_000, 3_000, 0.005)
        self.assertGreaterEqual(small, 0.0)
        self.assertGreaterEqual(large, 0.0)
        self.assertLess(large, small)

    def test_ucb_range_symmetry_and_reproducibility(self) -> None:
        labels = [0] * 40 + [1] * 60
        scores = [index / 100 for index in range(100)]
        first = two_sample_structural_certificates(labels, scores, 2, 0.05)
        second = two_sample_structural_certificates(labels, scores, 2, 0.05)
        self.assertEqual(first, second)
        self.assertEqual(first.direct[0][1], first.direct[1][0])
        self.assertTrue(all(0.0 <= value <= 1.0 for row in first.direct for value in row))

    def test_unsupported_class_uses_safe_fallback(self) -> None:
        certificate = two_sample_structural_certificates([0] * 20, list(range(20)), 2, 0.05)
        self.assertEqual(certificate.direct[0][1], 1.0)

    def test_deterministic_pair_matches_empirical_plus_formula_radius(self) -> None:
        first, second = [0.0, 0.0, 0.0, 0.0], [1.0, 1.0, 1.0, 1.0]
        certificate = two_sample_structural_certificates([0] * 4 + [1] * 4, first + second, 2, 0.05)
        expected = min(1.0, certificate.empirical_ks[0][1] + two_sample_ks_radius(4, 4, 0.05))
        self.assertEqual(certificate.direct[0][1], expected)

    def test_certificate_uses_structural_arguments_only(self) -> None:
        certificate = two_sample_structural_certificates([0] * 50 + [1] * 50, [0.0] * 100, 2, 0.05)
        self.assertEqual(certificate.counts, (50, 50))
