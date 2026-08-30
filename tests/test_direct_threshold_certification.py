import math
import unittest

from ordinal_aware_conformal.calibration.direct_threshold_certification import (
    binomial_survival,
    certify_fixed_threshold,
    clopper_pearson_lower,
    direct_pac_threshold,
    exact_acceptance_probability,
    minimum_successes_for_certification,
    proposal_quantile,
)


class DirectThresholdCertificationTests(unittest.TestCase):
    def test_exact_lower_bound_matches_known_clopper_pearson_value(self) -> None:
        # Beta(8, 3) 1% quantile, independently checked against scipy.stats.beta.ppf.
        self.assertAlmostEqual(clopper_pearson_lower(8, 10, 0.01), 0.38825714116242566, places=12)

    def test_zero_and_all_success_edge_cases(self) -> None:
        self.assertEqual(clopper_pearson_lower(0, 10, 0.01), 0.0)
        self.assertAlmostEqual(clopper_pearson_lower(10, 10, 0.01), 0.6309573444801932, places=12)

    def test_lower_bound_increases_with_successes(self) -> None:
        lower_bounds = [clopper_pearson_lower(successes, 20, 0.01) for successes in range(21)]
        self.assertEqual(lower_bounds, sorted(lower_bounds))

    def test_increasing_threshold_cannot_reduce_successes(self) -> None:
        data = [0.1, 0.3, 0.5, 0.9]
        low = certify_fixed_threshold(0.3, data, 0.90, 0.01)
        high = certify_fixed_threshold(0.8, data, 0.90, 0.01)
        self.assertLessEqual(low.successes, high.successes)

    def test_certification_does_not_include_proposal_scores(self) -> None:
        certification = certify_fixed_threshold(0.5, [0.1, 0.2, 0.8], 0.90, 0.01)
        self.assertEqual(certification.support, 3)
        self.assertEqual(certification.successes, 2)

    def test_rejected_candidate_returns_infinity(self) -> None:
        result = certify_fixed_threshold(0.1, [0.2] * 100, 0.90, 0.01)
        self.assertFalse(result.accepted)
        self.assertTrue(math.isinf(result.threshold))

    def test_proposal_rank_is_reproducible(self) -> None:
        self.assertEqual(proposal_quantile([1.0, 2.0, 3.0, 4.0], 0.75), 4.0)

    def test_same_inputs_produce_identical_certification(self) -> None:
        first = certify_fixed_threshold(0.7, [0.1, 0.3, 0.6, 0.9] * 30, 0.90, 0.01)
        second = certify_fixed_threshold(0.7, [0.1, 0.3, 0.6, 0.9] * 30, 0.90, 0.01)
        self.assertEqual(first, second)

    def test_direct_pac_uses_exact_required_order_statistic(self) -> None:
        values = list(range(100))
        result = direct_pac_threshold(values, 0.90, 0.01)
        required = minimum_successes_for_certification(100, 0.90, 0.01)
        self.assertEqual(result.successes, required)
        self.assertEqual(result.threshold, float(values[required - 1]))

    def test_binomial_acceptance_probability_agrees_with_monte_carlo(self) -> None:
        trials, probability = 100, 0.95
        expected = exact_acceptance_probability(trials, probability, 0.90, 0.01)
        import numpy as np

        rng = np.random.default_rng(20260828)
        required = minimum_successes_for_certification(trials, 0.90, 0.01)
        observed = (rng.binomial(trials, probability, size=100_000) >= required).mean()
        self.assertAlmostEqual(observed, expected, delta=0.005)
        self.assertAlmostEqual(binomial_survival(required, trials, probability), expected, places=12)
