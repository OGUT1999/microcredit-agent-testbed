import json
import unittest
from pathlib import Path

from qualification import validate


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
        data = record("PASS")
        for gate in data["gates"].values():
            gate["status"] = "verified"
            gate["chain_complete"] = True
        data["conservative_net_earnings_status"] = "positive"
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


if __name__ == "__main__":
    unittest.main()
