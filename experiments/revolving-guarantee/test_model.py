import math
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import model  # noqa: E402


class BreakEven(unittest.TestCase):
    def test_formula(self):
        # k* = (pG + c) / ((1 - p) q)
        self.assertAlmostEqual(model.break_even(0.18, 0.7, 60, 2), (0.18 * 60 + 2) / (0.82 * 0.7))

    def test_zero_drift_at_break_even(self):
        k = model.break_even(0.05, 0.7, 60, 2)
        self.assertAlmostEqual(model.drift(0.05, 0.7, 60, 2, k), 0.0, places=9)

    def test_rejects_bad_probabilities(self):
        with self.assertRaises(ValueError):
            model.break_even(1.0, 0.7, 60, 2)
        with self.assertRaises(ValueError):
            model.break_even(0.1, 0.0, 60, 2)


class Ruin(unittest.TestCase):
    def test_no_adjustment_coefficient_without_positive_drift(self):
        k = model.break_even(0.05, 0.7, 60, 2)
        self.assertIsNone(model.adjustment_coefficient(0.05, 0.7, 60, 2, k))

    def test_adjustment_coefficient_solves_lundberg_equation(self):
        p, q, G, c, k = 0.02, 0.9, 60, 1, 13.25
        R = model.adjustment_coefficient(p, q, G, c, k)
        value = ((1 - p) * q * math.exp(-R * (k - c)) + p * math.exp(R * (G + c))
                 + (1 - p) * (1 - q) * math.exp(R * c))
        self.assertAlmostEqual(value, 1.0, places=6)

    def test_break_even_pricing_is_usually_ruined(self):
        k = model.break_even(0.18, 0.7, 60, 2)
        ruin, _ = model.simulate(0.18, 0.7, 60, 2, k, jobs=1000, runs=400, seed=1)
        self.assertGreater(ruin, 0.8)

    def test_early_death_floor_matches_simulation(self):
        # Capital 100 < 2(G + c): one claim before the first contribution stops the pool.
        p, q = 0.18, 0.7
        ruin, _ = model.simulate(p, q, 60, 2, 1000.0, jobs=50, runs=4000, seed=3)
        self.assertAlmostEqual(ruin, model.early_death(p, q), delta=0.03)

    def test_deterministic(self):
        a = model.simulate(0.1, 0.8, 20, 1, 5, jobs=200, runs=200, seed=11)
        b = model.simulate(0.1, 0.8, 20, 1, 5, jobs=200, runs=200, seed=11)
        self.assertEqual(a, b)


class WorkerNet(unittest.TestCase):
    def test_insurance_variant_at_break_even_reduces_to_caused_gain_minus_cost(self):
        p, q, G, c, w = 0.05, 0.7, 60, 2, 60
        k = model.break_even(p, q, G, c)
        for a, s in [(0, 1), (0.3, 0.5), (1, 1)]:
            got = model.worker_net_per_job(p, q, G, c, k, w, a, s, refunds_to_workers=True)
            self.assertAlmostEqual(got, a * (1 - p) * s * w - c, places=9)

    def test_client_refund_variant_threshold(self):
        p, q, G, c, w = 0.18, 0.7, 60, 2, 60
        k = model.break_even(p, q, G, c)
        threshold = (p * G + c) / ((1 - p) * w)
        self.assertAlmostEqual(threshold, 0.26, places=2)
        below = model.worker_net_per_job(p, q, G, c, k, w, 0.5, 0.5, refunds_to_workers=False)
        above = model.worker_net_per_job(p, q, G, c, k, w, 0.6, 0.5, refunds_to_workers=False)
        self.assertLess(below, 0)
        self.assertGreater(above, 0)


if __name__ == "__main__":
    unittest.main()
