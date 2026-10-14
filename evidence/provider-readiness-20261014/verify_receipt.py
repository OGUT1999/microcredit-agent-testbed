#!/usr/bin/env python3
"""Reconcile this dated internal fixture, not live readiness or authority."""
from datetime import datetime, timezone
import json
from pathlib import Path
import unittest


def fresh_at(last_report, max_age, timestamp):
    if any(type(v) is not int or v < 0 for v in (last_report, max_age, timestamp)):
        raise ValueError("invalid fixture operands")
    if last_report > timestamp:
        raise ValueError("future report cannot establish observed freshness")
    return last_report != 0 and timestamp <= last_report + max_age


def reconcile(data):
    if not isinstance(data, dict) or data.get("chain_id") != 84532:
        raise ValueError("invalid fixture")
    fields = ("lender_cash_units", "target_lender_cash_units", "last_report_at",
              "max_score_age_seconds", "block_timestamp", "requested_read_limit")
    if any(type(data.get(k)) is not int or data[k] < 0 for k in fields):
        raise ValueError("invalid fixture operands")
    components = data.get("reported_read_components")
    if not isinstance(components, list) or not components or any(type(v) is not int or v < 0 for v in components):
        raise ValueError("invalid read components")
    expiry = data["last_report_at"] + data["max_score_age_seconds"]
    expiry_utc = datetime.fromtimestamp(expiry, timezone.utc).isoformat().replace("+00:00", "Z")
    day_start = datetime.fromisoformat(data["accepted_program_date"] + "T00:00:00+00:00")
    count = sum(components)
    return {
        "status": "DATED_OPERAND_RECONCILIATION_ONLY",
        "shortfall_test_usdc_units": max(0, data["target_lender_cash_units"] - data["lender_cash_units"]),
        "fresh_at_reported_pin": fresh_at(data["last_report_at"], data["max_score_age_seconds"], data["block_timestamp"]),
        "fresh_through_inclusive_utc": expiry_utc,
        "current_report_expires_before_program_date": expiry < int(day_start.timestamp()),
        "exact_program_time_established": False,
        "component_read_sum": count,
        "reported_total_conflicts_with_component_sum": count != data.get("reported_approximate_reads"),
        "reported_components_within_requested_bound": count <= data["requested_read_limit"],
        "exact_actual_read_count_verified": False,
        "independent_chain_authentication": False,
        "funding_established": False,
        "source5_recovery_verified": False,
        "transaction_authorized": False,
        "human_earnings_established": False,
    }


class BoundaryTests(unittest.TestCase):
    def test_last_second_inclusive(self):
        self.assertTrue(fresh_at(100, 10, 110))

    def test_next_second_stale(self):
        self.assertFalse(fresh_at(100, 10, 111))

    def test_zero_report_not_fresh(self):
        self.assertFalse(fresh_at(0, 10, 1))

    def test_future_report_rejected(self):
        with self.assertRaises(ValueError):
            fresh_at(101, 10, 100)

    def test_invalid_operands_rejected(self):
        for bad in (True, -1, 1.5, "100", None):
            with self.subTest(value=bad), self.assertRaises(ValueError):
                fresh_at(bad, 10, 110)

    def test_dated_fixture(self):
        data = json.loads(Path(__file__).with_name("receipt.json").read_text())
        out = reconcile(data)
        self.assertEqual(out["shortfall_test_usdc_units"], 185000000)
        self.assertEqual(out["fresh_through_inclusive_utc"], "2026-10-15T21:34:50Z")
        self.assertTrue(out["fresh_at_reported_pin"])
        self.assertTrue(out["current_report_expires_before_program_date"])
        self.assertEqual(out["component_read_sum"], 18)
        self.assertFalse(out["reported_components_within_requested_bound"])
        self.assertTrue(out["reported_total_conflicts_with_component_sum"])
        for flag in ("transaction_authorized", "human_earnings_established", "source5_recovery_verified", "funding_established"):
            self.assertFalse(out[flag])


if __name__ == "__main__":
    try:
        packet = json.loads(Path(__file__).with_name("receipt.json").read_text())
        print(json.dumps(reconcile(packet), indent=2))
    except (OSError, ValueError, KeyError, TypeError, OverflowError):
        print(json.dumps({"status": "INVALID_FIXTURE", "transaction_authorized": False}))
        raise SystemExit(1)
