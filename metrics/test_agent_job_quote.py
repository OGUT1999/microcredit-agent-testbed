"""Synthetic quote controls, not customers, observed costs or human outcomes."""
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from decimal import localcontext
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from agent_job_quote import analyze, main, READY, CASH, NONCASH, HOURS


def quote():
    def money(n):
        return {"amount": n, "currency": "SYNTHETIC_UNIT"}
    return {"currency": "SYNTHETIC_UNIT", "price_scope": "individual_gross",
            "cost_basis": "bounded_estimate", "basis_evidence": "synthetic control only",
            "price": money("100"), "fees": {"basis": "gross_individual_price",
              "platform_bps": 750, "evaluator_bps": 250},
            "cash_costs": {k: money("10" if k == "inference" else "0") for k in CASH},
            "worker_pay": money("10"),
            "owner_hours": {"delivery": "1", "rework": "0.25", "support_and_dispute": "0.25"},
            "owner_hourly_rate": money("10"),
            "noncash_costs": {k: money("5" if k != "other" else "0") for k in NONCASH},
            "all_costs_and_effort_bounded": True, "owner_hours_exclude_worker_hours": True,
            "worker_pay_excluded_from_other_costs": True}


class QuoteTests(unittest.TestCase):
    def test_exact_positive_control_and_no_input_mutation(self):
        data = quote(); before = deepcopy(data)
        r = analyze(data)
        self.assertEqual(r["status"], READY)
        self.assertEqual(data, before)
        a = r["arithmetic"]
        self.assertEqual((a["projected_post_percentage_fees"], a["projected_n_cash"],
                          a["projected_n_full"], a["full_cost_including_worker_pay"]),
                         ("90", "70", "50", "40"))
        self.assertEqual((a["worker_pay_once"], a["priced_owner_labor"]), ("10", "15"))
        for flag in ("offer_authorized", "funding_established", "settled_payment_established",
                     "human_earnings_established", "poverty_reduction_established", "financial_authority"):
            self.assertIs(r[flag], False)

    def test_every_unknown_amount_or_fee_suppresses_all_margin(self):
        paths = [("price", "amount"), ("worker_pay", "amount"), ("owner_hourly_rate", "amount")]
        paths += [("cash_costs", k, "amount") for k in CASH]
        paths += [("noncash_costs", k, "amount") for k in NONCASH]
        paths += [("owner_hours", k) for k in HOURS]
        paths += [("fees", k) for k in ("platform_bps", "evaluator_bps")]
        for path in paths:
            for value in (None,):
                data = quote(); target = data
                for k in path[:-1]: target = target[k]
                target[path[-1]] = value
                with self.subTest(path=path):
                    r = analyze(data)
                    self.assertEqual(r["status"], "INCOMPLETE_QUOTE")
                    self.assertIsNone(r["arithmetic"])

    def test_missing_sections_and_unpriced_owner_time_do_not_pass(self):
        for field in quote():
            data = quote(); del data[field]
            with self.subTest(field=field):
                self.assertEqual(analyze(data)["status"], "INCOMPLETE_QUOTE")
        data = quote(); data["owner_hourly_rate"]["amount"] = "0"
        self.assertEqual(analyze(data)["status"], "INCOMPLETE_QUOTE")

    def test_currency_mismatch_is_not_implicit_conversion(self):
        data = quote(); data["cash_costs"]["inference"]["currency"] = "ANOTHER_UNIT"
        r = analyze(data)
        self.assertEqual(r["status"], "INCOMPLETE_QUOTE")
        self.assertIsNone(r["arithmetic"])

    def test_pool_or_unknown_fee_basis_does_not_become_individual_price(self):
        for field, value in (("price_scope", "split_pool"), ("price_scope", "auction_maximum"),
                              ("cost_basis", "unknown")):
            data = quote(); data[field] = value
            self.assertEqual(analyze(data)["status"], "INCOMPLETE_QUOTE")
        data = quote(); data["fees"]["basis"] = "net_reward"
        self.assertEqual(analyze(data)["status"], "INCOMPLETE_QUOTE")

    def test_nonpositive_and_positive_but_under_management_bar(self):
        for cost, net in (("60", "0"), ("61", "-1"), ("20", "40")):
            data = quote(); data["cash_costs"]["inference"]["amount"] = cost
            r = analyze(data)
            self.assertEqual(r["status"], "ECONOMICS_NOT_MET")
            self.assertEqual(r["arithmetic"]["projected_n_full"], net)
        data = quote(); data["cash_costs"]["inference"]["amount"] = "15"
        self.assertEqual(analyze(data)["status"], READY)  # exactly half of post-fee90

    def test_explicit_fee_rates_not_historical_045_default(self):
        for bps, projected in ((0, "100"), (750, "185/2"), (1000, "90"), (10000, "0")):
            data = quote(); data["fees"].update(platform_bps=bps, evaluator_bps=0)
            r = analyze(data)
            self.assertEqual(r["arithmetic"]["projected_post_percentage_fees"], projected)
        for bps in (-1, 10001, True, "750", 7.5):
            data = quote(); data["fees"]["platform_bps"] = bps
            with self.assertRaises(ValueError): analyze(data)
        data = quote(); data["fees"].update(platform_bps=9000, evaluator_bps=2000)
        with self.assertRaises(ValueError): analyze(data)

    def test_bounded_exact_amount_grammar_and_decimal_context_independence(self):
        for value in (-1, True, 1.2, "NaN", "Infinity", "1e2", " 2", "1/2", "1_000",
                      "9" * 19, "0." + "1" * 13):
            data = quote(); data["price"]["amount"] = value
            with self.subTest(value=value), self.assertRaises(ValueError): analyze(data)
        data = quote(); data["cash_costs"]["inference"]["amount"] = "10.000000000001"
        with localcontext() as c:
            c.prec = 2
            self.assertEqual(analyze(data)["arithmetic"]["projected_n_full"], "49999999999999/1000000000000")

    def test_unbounded_support_or_double_count_declarations_block_review(self):
        for key in ("all_costs_and_effort_bounded", "owner_hours_exclude_worker_hours",
                    "worker_pay_excluded_from_other_costs"):
            data = quote(); data[key] = False
            self.assertEqual(analyze(data)["status"], "INCOMPLETE_QUOTE")
            data[key] = "yes"
            with self.assertRaises(ValueError): analyze(data)

    def test_cli_private_errors_and_labels_with_shared_reader(self):
        with tempfile.TemporaryDirectory(prefix="PRIVATE_SENTINEL_") as directory:
            path = Path(directory) / "quote.json"
            valid = json.dumps(quote()).replace("SYNTHETIC_UNIT", "PRIVATE_SENTINEL")
            for content, status, rc in ((valid, READY, 0), ("{}", "INCOMPLETE_QUOTE", 1),
                     (valid[:-1] + ',"price":{}}', "INVALID_QUOTE", 2),
                     ('{"PRIVATE_SENTINEL":1}', "INVALID_QUOTE", 2),
                     ('{"price":NaN}', "INVALID_QUOTE", 2),
                     ("[" * 2000, "INVALID_QUOTE", 2)):
                path.write_text(content, encoding="utf-8")
                out, err = io.StringIO(), io.StringIO()
                with redirect_stdout(out), redirect_stderr(err):
                    actual = main([str(path)])
                self.assertEqual((actual, json.loads(out.getvalue())["status"]), (rc, status))
                self.assertNotIn("PRIVATE_SENTINEL", out.getvalue() + err.getvalue())
            out = io.StringIO()
            with redirect_stdout(out): self.assertEqual(main([directory + "/missing"]), 2)
            self.assertNotIn("PRIVATE_SENTINEL", out.getvalue())

    def test_cli_runs_from_unrelated_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "quote.json"; path.write_text(json.dumps(quote()))
            p = subprocess.run([sys.executable, str(Path(__file__).with_name("agent_job_quote.py")), str(path)],
                               cwd=directory, text=True, capture_output=True, timeout=10)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(json.loads(p.stdout)["status"], READY)


if __name__ == "__main__":
    unittest.main()
