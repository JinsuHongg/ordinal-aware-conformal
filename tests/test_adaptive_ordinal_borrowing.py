from math import inf
import unittest

from ordinal_aware_conformal.calibration.adaptive_ordinal_borrowing import (
    NeighborhoodSelection,
    StructuralCertificates,
    fit_adaptive_ordinal_borrowing,
    fit_independent_mondrian,
    select_neighborhoods,
    structural_certificates,
)


class AdaptiveOrdinalBorrowingTests(unittest.TestCase):
    def test_h_zero_certified_reduces_to_independent_mondrian(self) -> None:
        labels = [0] * 10 + [1] * 10
        scores = [float(index) for index in range(20)]
        certificates = structural_certificates(labels, scores, 2, 0.05)
        selection = select_neighborhoods(certificates, 20, 0.10, radii=(0,))
        certified = fit_adaptive_ordinal_borrowing(labels, scores, 0.10, 2, selection, certified=True)
        mondrian = fit_independent_mondrian(labels, scores, 0.10, 2)
        self.assertEqual(selection.epsilons, (0.0, 0.0))
        self.assertEqual(certified.ranks, mondrian.ranks)
        self.assertEqual(certified.thresholds, mondrian.thresholds)

    def test_independent_infinite_rank_convention(self) -> None:
        result = fit_independent_mondrian([0] * 5, [1.0] * 5, 0.10, 1)
        self.assertEqual(result.thresholds[0], inf)
        self.assertIsNone(result.ranks[0])

    def test_finite_certified_pooled_rank(self) -> None:
        labels, scores = [0] * 100, list(map(float, range(100)))
        selection = NeighborhoodSelection((0,), (0.03,), (100.0,), (0.03,))
        result = fit_adaptive_ordinal_borrowing(labels, scores, 0.10, 1, selection, certified=True)
        self.assertEqual(result.ranks, (94,))  # ceil(101 * 0.93)
        self.assertEqual(result.thresholds, (93.0,))

    def test_unsupported_structural_class_suppresses_borrowing(self) -> None:
        certificates = structural_certificates([0] * 20, [float(i) for i in range(20)], 2, 0.05)
        self.assertEqual(certificates.direct[0][1], 1.0)
        selection = select_neighborhoods(certificates, 100, 0.10)
        self.assertEqual(selection.radii, (0, 0))

    def test_final_certificate_is_minimum_of_direct_and_path(self) -> None:
        certificates = structural_certificates([0] * 30 + [1] * 30 + [2] * 30, list(range(90)), 3, 0.05)
        for first in range(3):
            for second in range(3):
                self.assertEqual(certificates.delta[first][second], min(certificates.direct[first][second], certificates.path[first][second]))

    def test_selection_does_not_depend_on_final_scores(self) -> None:
        certificates = structural_certificates([0] * 100 + [1] * 100, [0.0] * 200, 2, 0.05)
        first = select_neighborhoods(certificates, 400, 0.10)
        # Selection accepts no final labels or score values by interface.
        second = select_neighborhoods(certificates, 400, 0.10)
        self.assertEqual(first, second)

    def test_reproducible_structural_calculation(self) -> None:
        labels, scores = [0] * 25 + [1] * 25, [float(index) / 50 for index in range(50)]
        self.assertEqual(structural_certificates(labels, scores, 2, 0.05), structural_certificates(labels, scores, 2, 0.05))

