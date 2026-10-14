import json
import copy
import unittest
from pathlib import Path

from qualification import payout_readiness, validate


def cash_economics():
    return {"basis": "cash", "currency": "SLE", "currency_unit_confirmed": True,
            "currency_source_ids": ["s2"], "gross_cash_min": "20",
            "gross_source_ids": ["s2"],
            "costs": {"provider_transfer_fee": "0", "recipient_cashout_fee": "1.53",
                      "other_worker_costs": "2"},
            "cost_source_ids": {n: ["s2"] for n in
                                ("provider_transfer_fee", "recipient_cashout_fee", "other_worker_costs")}}


def pass_record():
    data = record("PASS")
    for gate in data["gates"].values():
        gate.update(status="verified", chain_complete=True)
    data["gates"]["current_demand"]["source_ids"] = ["s2"]
    data["conservative_net_earnings_status"] = "positive"
    data["payout_economics"] = cash_economics()
    return data


def points_record():
    data = pass_record()
    payout = data["payout_economics"]
    payout.pop("gross_cash_min")
    payout.update(basis="points", task_points_min="1000", fixed_conversion_confirmed=True,
                  conversion_source_ids=["s2"], quotes=[
                      {"id": "a", "points_min": "1000", "points_max": "1000",
                       "cash_min": "20", "cash_max": "20", "currency": "SLE", "source_ids": ["s2"]},
                      {"id": "b", "points_min": "2500", "points_max": "5000",
                       "cash_min": "50", "cash_max": "100", "currency": "SLE", "source_ids": ["s2"]}])
    return data


def record(decision="NO_VERIFIABLE_ROUTE"):
    gates = {
        "current_access": {"status": "verified", "chain_complete": True, "source_ids": ["s1"], "finding": "access"},
        "current_demand": {"status": "unverified", "chain_complete": False, "source_ids": ["s1"], "finding": "no current task"},
        "worker_eligibility": {"status": "verified", "chain_complete": True, "source_ids": ["s2"], "finding": "eligible"},
        "spendable_payout": {"status": "unverified", "chain_complete": False, "source_ids": ["s2"], "finding": "no local route"},
    }
    return {
        "schema_version": 1,
        "candidate_id": "candidate",
        "candidate_name": "Candidate",
        "country": "Sierra Leone",
        "checked_at": "2026-10-13T19:00:00Z",
        "decision": decision,
        "resource_bound": {"contact": 0, "spend_usd": 0, "signups": 0},
        "sources": [
            {"id": "s1", "kind": "original", "url": "https://example.org/a", "checked_at": "2026-10-13T19:00:00Z", "supports": "a", "does_not_establish": "b"},
            {"id": "s2", "kind": "original", "url": "https://example.net/b", "checked_at": "2026-10-13T19:00:00Z", "supports": "b", "does_not_establish": "a"},
        ],
        "gates": gates,
        "independent_reviews": [
            {"reviewer": "agent:codex", "source_check": "original", "disposition": decision, "receipt_url": "https://github.com/example/repo/issues/1#issuecomment-1"},
            {"reviewer": "agent:claude", "source_check": "original", "disposition": decision, "receipt_url": "https://github.com/example/repo/issues/1#issuecomment-2"},
        ],
        "conservative_net_earnings_status": "unknown",
        "limitations": "This is not evidence of unavailability.",
        "next_trigger": "Current task and payout evidence",
    }


class QualificationTests(unittest.TestCase):
    def test_negative_record_passes(self):
        self.assertEqual(validate(record()), [])

    def test_in_review_record_preserves_one_screen(self):
        data = record("IN_REVIEW")
        data["independent_reviews"] = data["independent_reviews"][:1]
        self.assertEqual(validate(data), [])

    def test_pass_requires_all_gates_and_positive_net(self):
        data = pass_record()
        self.assertEqual(validate(data), [])

    def test_false_pass_is_rejected(self):
        data = record("PASS")
        errors = validate(data)
        self.assertTrue(any("every required gate" in error for error in errors))
        self.assertTrue(any("positive conservative" in error for error in errors))

    def test_generic_or_historical_evidence_cannot_complete_pass_chain(self):
        data = record("PASS")
        for gate in data["gates"].values():
            gate["status"] = "verified"
        data["conservative_net_earnings_status"] = "positive"
        self.assertTrue(any("complete evidence chain" in error for error in validate(data)))

    def test_negative_needs_independent_reviewers(self):
        data = record()
        data["independent_reviews"] = data["independent_reviews"][:1]
        self.assertTrue(any("2 attributable" in error for error in validate(data)))

    def test_negative_cannot_claim_unavailable(self):
        data = record()
        data["limitations"] = "The platform is unavailable."
        self.assertTrue(any("unavailability claim" in error for error in validate(data)))

    def test_unknown_source_reference_is_rejected(self):
        data = record()
        data["gates"]["current_demand"]["source_ids"] = ["missing"]
        self.assertTrue(any("unknown source" in error for error in validate(data)))

    def test_unverified_gate_cannot_claim_complete_chain(self):
        data = record("IN_REVIEW")
        data["independent_reviews"] = data["independent_reviews"][:1]
        data["gates"]["current_demand"]["chain_complete"] = True
        self.assertTrue(any("verified exactly" in error for error in validate(data)))

    def test_case_aliased_reviewers_are_duplicates(self):
        data = record()
        data["independent_reviews"][1]["reviewer"] = "Agent:Codex"
        self.assertTrue(any("duplicate reviewer" in error for error in validate(data)))

    def test_reviewer_must_use_canonical_agent_id(self):
        data = record()
        data["independent_reviews"][0]["reviewer"] = "codex"
        self.assertTrue(any("canonical agent:" in error for error in validate(data)))

    def test_github_homepage_is_not_a_review_receipt(self):
        data = record()
        data["independent_reviews"][0]["receipt_url"] = "https://github.com/"
        self.assertTrue(any("issue or PR comment" in error for error in validate(data)))

    def test_net_earnings_status_is_an_enum(self):
        data = record()
        data["conservative_net_earnings_status"] = {"estimate": "unknown"}
        self.assertTrue(any("must be positive" in error for error in validate(data)))

    def test_every_committed_sierra_leone_packet_validates(self):
        packet_dir = Path(__file__).resolve().parent
        packets = sorted(packet_dir.glob("*-sierra-leone-*.json"))
        self.assertGreaterEqual(len(packets), 2)
        for packet in packets:
            with self.subTest(packet=packet.name):
                self.assertEqual(validate(json.loads(packet.read_text(encoding="utf-8"))), [])

    def test_positive_label_without_quote_rejected(self):
        data = pass_record(); del data["payout_economics"]
        self.assertTrue(any("positive-net label" in e for e in validate(data)))

    def test_exact_cash_net_not_human_earnings(self):
        result = payout_readiness(pass_record())
        self.assertEqual(result["net_cash_lower_bound"], "1647/100")
        self.assertFalse(result["human_earnings_established"])
        self.assertFalse(result["financial_authority"])

    def test_points_reuses_consistency_helper(self):
        data = points_record()
        self.assertEqual(validate(data), [])
        self.assertEqual(payout_readiness(data)["net_cash_lower_bound"], "1647/100")

    def test_disjoint_conversion_cannot_pass(self):
        data = points_record()
        data["payout_economics"]["quotes"][0].update(cash_min="1000", cash_max="1000")
        self.assertTrue(any("INCONSISTENT_QUOTE" in e for e in validate(data)))

    def test_fieldwork_source_fixture_cannot_pass(self):
        data = points_record()
        fixture = json.loads(Path(__file__).with_name("fieldwork-quote-regression-2026-10-13.json").read_text())
        data["payout_economics"].update(fixture)
        self.assertTrue(any("INCOMPLETE_QUOTE" in e for e in validate(data)))

    def test_unknown_worker_costs_never_default_zero(self):
        for basis in (pass_record, points_record):
            for name in cash_economics()["costs"]:
                for mode in ("missing", "null"):
                    data = basis()
                    if mode == "missing": del data["payout_economics"]["costs"][name]
                    else: data["payout_economics"]["costs"][name] = None
                    with self.subTest(basis=basis.__name__, name=name, mode=mode):
                        self.assertTrue(validate(data))

    def test_legacy_labels_not_normalized(self):
        data = points_record(); data["payout_economics"]["currency"] = "SLL"
        self.assertTrue(any("match payout unit" in e for e in validate(data)))

    def test_literal_confirmation_only(self):
        for field in ("currency_unit_confirmed", "fixed_conversion_confirmed"):
            for value in (1, "true", False, None):
                data = points_record(); data["payout_economics"][field] = value
                self.assertTrue(validate(data))

    def test_quote_and_cost_sources_tied_to_payout_gate(self):
        for field in ("currency_source_ids", "gross_source_ids", "conversion_source_ids"):
            data = points_record(); data["payout_economics"][field] = ["s1"]
            self.assertTrue(validate(data))
        data = points_record(); data["payout_economics"]["quotes"][0]["source_ids"] = ["s1"]
        self.assertTrue(validate(data))
        data = pass_record(); data["payout_economics"]["cost_source_ids"]["recipient_cashout_fee"] = []
        self.assertTrue(validate(data))

    def test_zero_or_negative_net_rejected(self):
        for gross in ("3.53", "3", "0"):
            data = pass_record(); data["payout_economics"]["gross_cash_min"] = gross
            self.assertTrue(any("strictly positive" in e for e in validate(data)))

    def test_invalid_gross_and_fee_amounts_fail_closed(self):
        for value in (True, 1.5, "NaN", "-1", "1e2"):
            data = pass_record(); data["payout_economics"]["gross_cash_min"] = value
            self.assertTrue(validate(data))
            data = pass_record(); data["payout_economics"]["costs"]["recipient_cashout_fee"] = value
            self.assertTrue(validate(data))

    def test_cash_label_cannot_hide_conversion(self):
        data = points_record(); data["payout_economics"].update(basis="cash", gross_cash_min="1000")
        self.assertTrue(any("cannot bypass" in e for e in validate(data)))

    def test_arithmetic_does_not_complete_other_evidence_gates(self):
        data = pass_record(); data["gates"]["current_demand"].update(status="unverified", chain_complete=False)
        self.assertTrue(any("every required gate" in e for e in validate(data)))

    def test_unrelated_gross_source_does_not_complete_task_chain(self):
        data = pass_record(); data["gates"]["current_demand"]["source_ids"] = ["s1"]
        self.assertTrue(any("share a source with current_demand" in e for e in validate(data)))

    def test_no_input_mutation(self):
        data = points_record(); before = copy.deepcopy(data)
        validate(data)
        self.assertEqual(data, before)

    def test_independent_range_endpoints_and_intersection(self):
        data = points_record()
        data["payout_economics"].update(task_points_min="10", quotes=[
            {"id": "a", "points_min": "10", "points_max": "20", "cash_min": "100",
             "cash_max": "200", "currency": "SLE", "source_ids": ["s2"]},
            {"id": "b", "points_min": "10", "points_max": "10", "cash_min": "100",
             "cash_max": "100", "currency": "SLE", "source_ids": ["s2"]}])
        self.assertEqual(validate(data), [])
        self.assertEqual(payout_readiness(data)["net_cash_lower_bound"], "9647/100")

    def test_invalid_points_and_shapes_fail_closed(self):
        for value in (True, 1.5, "NaN", "-1", "1e2", None):
            data = points_record(); data["payout_economics"]["task_points_min"] = value
            self.assertTrue(validate(data))
        for field in ("costs", "cost_source_ids", "quotes", "currency_source_ids"):
            for value in (None, True, [], [None], {"wrong": []}):
                data = points_record(); data["payout_economics"][field] = value
                self.assertTrue(validate(data))


if __name__ == "__main__":
    unittest.main()
