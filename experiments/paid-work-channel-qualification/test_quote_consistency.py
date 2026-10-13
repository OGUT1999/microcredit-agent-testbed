import copy
import json
from pathlib import Path
import unittest

from quote_consistency import analyze


def consistent():
    return {"currency_unit_confirmed": True,
            "quotes": [{"id": "a", "points_min": "1000", "points_max": "1000",
                        "cash_min": "20", "cash_max": "20", "currency": "SLE"},
                       {"id": "b", "points_min": "2500", "points_max": "5000",
                        "cash_min": "50", "cash_max": "100", "currency": "SLE"}],
            "costs": {"provider_transfer_fee": "0", "recipient_cashout_fee": "1.53",
                      "other_worker_costs": "2"}}


class QuoteTests(unittest.TestCase):
    def test_consistent_not_a_channel_pass(self):
        r = analyze(consistent())
        self.assertEqual(r["status"], "QUOTE_ARITHMETIC_CONSISTENT")
        self.assertFalse(r["channel_pass"])
        self.assertFalse(r["human_earnings_established"])

    def test_source_fixture_unconfirmed_and_disjoint(self):
        d = json.loads(Path(__file__).with_name("fieldwork-quote-regression-2026-10-13.json").read_text())
        r = analyze(d)
        self.assertEqual(r["status"], "INCOMPLETE_QUOTE")
        self.assertFalse(r["fixed_rate_compatible"])
        self.assertEqual(r["rate_intervals"][0]["low_cash_per_point"], "1/100")
        self.assertEqual(r["rate_intervals"][0]["high_cash_per_point"], "1/10")

    def test_same_unit_assumption_explicit(self):
        d = consistent()
        d["quotes"][0]["cash_min"] = d["quotes"][0]["cash_max"] = "1000"
        self.assertEqual(analyze(d)["status"], "INCONSISTENT_QUOTE")

    def test_ranges_not_endpoint_pairs(self):
        r = analyze(consistent())
        self.assertEqual(r["rate_intervals"][1]["low_cash_per_point"], "1/100")
        self.assertEqual(r["rate_intervals"][1]["high_cash_per_point"], "1/25")

    def test_legacy_currency_not_normalized(self):
        d = consistent()
        d["quotes"][1]["currency"] = "SLL"
        self.assertEqual(analyze(d)["status"], "INCOMPLETE_QUOTE")
        self.assertIsNone(analyze(d)["fixed_rate_compatible"])

    def test_confirmation_literal_true_only(self):
        for v in ("yes", "true", 1, [], {}, None):
            d = consistent(); d["currency_unit_confirmed"] = v
            self.assertEqual(analyze(d)["status"], "INCOMPLETE_QUOTE")

    def test_unknown_recipient_cost_not_zero(self):
        d = consistent(); d["costs"]["recipient_cashout_fee"] = None
        self.assertEqual(analyze(d)["status"], "INCOMPLETE_QUOTE")
        self.assertFalse(analyze(d)["full_worker_costs_known"])

    def test_missing_costs_unknown(self):
        d = consistent(); del d["costs"]
        self.assertEqual(analyze(d)["status"], "INCOMPLETE_QUOTE")

    def test_invalid_numbers_fail_closed(self):
        for v in (True, 1.5, "NaN", "Infinity", "1e99", "-1", None, "9" * 19):
            d = consistent(); d["quotes"][0]["points_min"] = v
            self.assertEqual(analyze(d)["status"], "INVALID_QUOTE")

    def test_zero_points_invalid(self):
        d = consistent(); d["quotes"][0]["points_min"] = "0"
        self.assertEqual(analyze(d)["status"], "INVALID_QUOTE")

    def test_inverted_bounds_invalid(self):
        for low, high in (("points_min", "points_max"), ("cash_min", "cash_max")):
            d = consistent(); d["quotes"][0][low] = "10000"; d["quotes"][0][high] = "1"
            self.assertEqual(analyze(d)["status"], "INVALID_QUOTE")

    def test_duplicate_ids_invalid(self):
        d = consistent(); d["quotes"][1]["id"] = "a"
        self.assertEqual(analyze(d)["status"], "INVALID_QUOTE")

    def test_bad_shapes_invalid(self):
        for d in (None, [], {}, {"quotes": [None, None]}, {"quotes": []}):
            self.assertEqual(analyze(d)["status"], "INVALID_QUOTE")

    def test_negative_fee_invalid(self):
        d = consistent(); d["costs"]["provider_transfer_fee"] = "-1"
        self.assertEqual(analyze(d)["status"], "INVALID_QUOTE")

    def test_no_input_mutation(self):
        d = consistent(); before = copy.deepcopy(d)
        analyze(d)
        self.assertEqual(d, before)


if __name__ == "__main__":
    unittest.main()
