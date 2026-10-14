"""Exact bounded synthetic cash controls, never worker-income evidence."""
from copy import deepcopy
from decimal import localcontext, Inexact, Rounded, Overflow
from fractions import Fraction
import json
from pathlib import Path
import random
import unittest

from human_outcome_gate import classify, COST_CATEGORIES, READY, UNKNOWN
from test_human_outcome_gate import packet
import test_human_outcome_cli as cli_tests

ROOT = Path(__file__).resolve().parents[1]


class ExactCashTests(unittest.TestCase):
    def arithmetic(self, data):
        return classify(data)["reported_earnings_arithmetic"]

    def test_immutable_precision_falsifier_now_yields_exact_cent(self):
        path = ROOT / "evidence/human-outcome-cli-privacy-20261014/precision-limitation.json"
        before = path.read_bytes()
        receipt = json.loads(before)
        data = packet()
        data["job"]["payout"]["amount"] = receipt["received"]
        data["job"]["worker_costs"]["other"]["amount"] = receipt["additional_cost"]
        result = self.arithmetic(data)
        self.assertEqual(result["net_cash"], "0.01")
        self.assertEqual(Fraction(result["net_cash"]), Fraction(receipt["exact_net_rational"]))
        self.assertEqual(receipt["reported_net"], "0")  # Historical failure stays recorded.
        self.assertEqual(path.read_bytes(), before)

    def test_decimal_precision_rounding_traps_and_flags_cannot_change_cash(self):
        data = packet()
        data["job"]["payout"]["amount"] = "10000000000000000000000000000"
        data["job"]["worker_costs"]["other"]["amount"] = "9999999999999999999999999999.99"
        expected = self.arithmetic(data)
        for precision in (1, 2, 7, 28, 100):
            with localcontext() as context:
                context.prec = precision
                context.Emax, context.Emin = 2, -2
                for signal in (Inexact, Rounded, Overflow):
                    context.traps[signal] = True
                context.clear_flags()
                self.assertEqual(self.arithmetic(data), expected)
                self.assertFalse(any(context.flags.values()))

    def test_all_six_costs_aggregate_exactly_and_not_twice(self):
        data = packet()
        data["job"]["payout"]["amount"] = "1"
        for index, key in enumerate(COST_CATEGORIES):
            data["job"]["worker_costs"][key].update(
                amount="0.01", already_deducted_from_payout=index % 2 == 0)
        r = self.arithmetic(data)
        self.assertEqual(r["worker_costs_already_deducted"], "0.03")
        self.assertEqual(r["additional_worker_cash_costs"], "0.03")
        self.assertEqual(r["net_cash"], "0.97")

    def test_zero_and_negative_smallest_unit_retained(self):
        for received, cost, expected in (("0", "0.000000000001", "-0.000000000001"),
                                         ("0.0100", "0.01", "0"),
                                         ("0.000000000001", "0", "0.000000000001")):
            data = packet()
            data["job"]["payout"]["amount"] = received
            data["job"]["worker_costs"]["other"]["amount"] = cost
            self.assertEqual(self.arithmetic(data)["net_cash"], expected)
            self.assertEqual(classify(data)["earned_income_packet"]["state"], READY)

    def test_maximum_per_operand_and_aggregate_carry_are_exact(self):
        value = "9" * 32 + "." + "9" * 12
        data = packet()
        data["job"]["payout"]["amount"] = value
        for key in COST_CATEGORIES:
            data["job"]["worker_costs"][key]["amount"] = value
        r = self.arithmetic(data)
        self.assertEqual(Fraction(r["additional_worker_cash_costs"]), 6 * Fraction(value))
        self.assertEqual(Fraction(r["net_cash"]), -5 * Fraction(value))
        self.assertNotIn("/", r["net_cash"])
        self.assertNotIn("e", r["net_cash"])

    def test_oversize_exponent_special_sign_and_non_decimal_inputs_reject(self):
        invalid = ("1" * 33, 10 ** 32, "0." + "1" * 13, "1e2", "1e-1000000",
                   "+1", "-0", " 1", "1 ", "1_000", "1/2", ".5", "1.",
                   "NaN", "Infinity", "-1", "\u0661", True, 1.1)
        for value in invalid:
            for target in ("received", "cost"):
                data = packet()
                if target == "received":
                    data["job"]["payout"]["amount"] = value
                else:
                    data["job"]["worker_costs"]["other"]["amount"] = value
                with self.subTest(value=type(value).__name__, target=target):
                    with self.assertRaises(ValueError):
                        classify(data)

    def test_common_amount_grammar_applies_to_time_welfare_and_person_days(self):
        for section, key in (("job", "time_hours"), ("baseline", "amount"),
                             ("followup", "person_days"), ("poverty_line", "amount")):
            data = packet(); data[section][key] = "1e1000000"
            with self.assertRaises(ValueError):
                classify(data)

    def test_missing_cost_or_evidence_still_suppresses_arithmetic(self):
        for field in ("amount", "evidence", "already_deducted_from_payout"):
            data = packet(); del data["job"]["worker_costs"]["other"][field]
            r = classify(data)
            self.assertEqual(r["earned_income_packet"]["state"], UNKNOWN)
            self.assertNotIn("reported_earnings_arithmetic", r)

    def test_input_not_mutated_and_original_readiness_guards_preserved(self):
        data = packet(); data["job"]["payout"]["amount"] = "001000.000"
        before = deepcopy(data)
        self.assertEqual(self.arithmetic(data)["settled_wage_received"], "1000")
        self.assertEqual(data, before)
        data["job"]["consent"] = False
        self.assertNotIn("reported_earnings_arithmetic", classify(data))
        data["job"]["consent"] = True
        data["job"]["payout"]["settled"] = False
        self.assertNotIn("reported_earnings_arithmetic", classify(data))

    def test_seeded_integer_scale_oracle_for_cost_split_and_sign(self):
        rng = random.Random(20261014)
        for _ in range(100):
            data = packet()
            received = rng.randrange(0, 10 ** 36)
            to_text = lambda units: str(units // 10 ** 12) + "." + str(units % 10 ** 12).zfill(12)
            data["job"]["payout"]["amount"] = to_text(received)
            totals = [0, 0]
            for key in COST_CATEGORIES:
                cost, deducted = rng.randrange(0, 10 ** 36), bool(rng.randrange(2))
                data["job"]["worker_costs"][key].update(amount=to_text(cost),
                                                       already_deducted_from_payout=deducted)
                totals[int(deducted)] += cost
            r = self.arithmetic(data)
            self.assertEqual(Fraction(r["worker_costs_already_deducted"]), Fraction(totals[1], 10 ** 12))
            self.assertEqual(Fraction(r["additional_worker_cash_costs"]), Fraction(totals[0], 10 ** 12))
            self.assertEqual(Fraction(r["net_cash"]), Fraction(received - totals[0], 10 ** 12))

    def test_cli_exact_cent_and_invalid_bounds_keep_private_error_flags(self):
        runner = cli_tests.OutcomeCLITests()
        data = packet()
        data["job"]["payout"]["amount"] = "10000000000000000000000000000"
        data["job"]["worker_costs"]["other"]["amount"] = "9999999999999999999999999999.99"
        rc, result = runner.from_data(data)
        self.assertEqual(rc, 0)
        self.assertEqual(result["reported_earnings_arithmetic"]["net_cash"], "0.01")
        data["job"]["payout"]["amount"] = "PRIVATE_SENTINEL_" + "1" * 33
        rc, result = runner.from_data(data)
        self.assertEqual((rc, result["status"]), (2, "INVALID_PACKET"))


if __name__ == "__main__":
    unittest.main()
