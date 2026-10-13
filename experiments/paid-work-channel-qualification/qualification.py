#!/usr/bin/env python3
"""Validate a bounded paid-work channel qualification record.

This is an evidence sufficiency gate, not a market-access probe. It never logs in,
contacts a platform, spends money, or treats an unverified route as unavailable.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

REQUIRED_GATES = ("current_access", "current_demand", "worker_eligibility", "spendable_payout")
ALLOWED_GATE_STATES = {"verified", "unverified", "failed"}
ALLOWED_DECISIONS = {"IN_REVIEW", "PASS", "NO_VERIFIABLE_ROUTE"}
ALLOWED_NET_STATES = {"positive", "unknown", "nonpositive"}
GITHUB_RECEIPT = re.compile(
    r"^/[^/]+/[^/]+/(?:issues|pull)/[1-9][0-9]*(?:#issuecomment-[1-9][0-9]*|#discussion_r[1-9][0-9]*)$"
)


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate(record: dict) -> list[str]:
    errors: list[str] = []
    _require(record.get("schema_version") == 1, "schema_version must be 1", errors)
    for field in ("candidate_id", "candidate_name", "country", "checked_at", "decision", "limitations", "next_trigger"):
        _require(isinstance(record.get(field), str) and bool(record[field].strip()), f"{field} is required", errors)
    _require(record.get("decision") in ALLOWED_DECISIONS,
             "decision must be IN_REVIEW, PASS or NO_VERIFIABLE_ROUTE", errors)
    _require(record.get("country") == "Sierra Leone", "this bounded packet is for Sierra Leone", errors)
    _require(record.get("resource_bound") == {"contact": 0, "spend_usd": 0, "signups": 0},
             "resource_bound must preserve zero contact, spend and signup", errors)

    sources = record.get("sources")
    _require(isinstance(sources, list) and len(sources) >= 2, "at least two original-source records are required", errors)
    source_ids: set[str] = set()
    if isinstance(sources, list):
        for index, source in enumerate(sources):
            _require(isinstance(source, dict), f"sources[{index}] must be an object", errors)
            if not isinstance(source, dict):
                continue
            source_id = source.get("id")
            _require(isinstance(source_id, str) and bool(source_id), f"sources[{index}].id is required", errors)
            if isinstance(source_id, str):
                _require(source_id not in source_ids, f"duplicate source id {source_id}", errors)
                source_ids.add(source_id)
            _require(source.get("kind") == "original", f"sources[{index}] must be original", errors)
            url = source.get("url", "")
            parsed = urlparse(url) if isinstance(url, str) else None
            _require(bool(parsed and parsed.scheme == "https" and parsed.netloc), f"sources[{index}].url must be https", errors)
            for field in ("checked_at", "supports", "does_not_establish"):
                _require(isinstance(source.get(field), str) and bool(source[field].strip()),
                         f"sources[{index}].{field} is required", errors)

    gates = record.get("gates")
    _require(isinstance(gates, dict), "gates must be an object", errors)
    if isinstance(gates, dict):
        _require(set(gates) == set(REQUIRED_GATES), f"gates must be exactly {', '.join(REQUIRED_GATES)}", errors)
        for gate_name in REQUIRED_GATES:
            gate = gates.get(gate_name, {})
            _require(isinstance(gate, dict), f"gate {gate_name} must be an object", errors)
            if not isinstance(gate, dict):
                continue
            _require(gate.get("status") in ALLOWED_GATE_STATES, f"gate {gate_name} has invalid status", errors)
            _require(isinstance(gate.get("chain_complete"), bool),
                     f"gate {gate_name}.chain_complete must be boolean", errors)
            if gate.get("status") in ALLOWED_GATE_STATES and isinstance(gate.get("chain_complete"), bool):
                _require((gate["status"] == "verified") == gate["chain_complete"],
                         f"gate {gate_name} must be verified exactly when its evidence chain is complete", errors)
            refs = gate.get("source_ids")
            _require(isinstance(refs, list) and len(refs) >= 1, f"gate {gate_name} needs source_ids", errors)
            if isinstance(refs, list):
                for source_id in refs:
                    _require(source_id in source_ids, f"gate {gate_name} references unknown source {source_id}", errors)
            _require(isinstance(gate.get("finding"), str) and bool(gate["finding"].strip()),
                     f"gate {gate_name}.finding is required", errors)

    reviews = record.get("independent_reviews")
    required_reviews = 1 if record.get("decision") == "IN_REVIEW" else 2
    _require(isinstance(reviews, list) and len(reviews) >= required_reviews,
             f"{required_reviews} attributable original-source review(s) required", errors)
    reviewers: set[str] = set()
    if isinstance(reviews, list):
        for index, review in enumerate(reviews):
            _require(isinstance(review, dict), f"independent_reviews[{index}] must be an object", errors)
            if not isinstance(review, dict):
                continue
            reviewer = review.get("reviewer")
            _require(isinstance(reviewer, str) and bool(reviewer), f"review[{index}].reviewer is required", errors)
            if isinstance(reviewer, str):
                canonical_reviewer = reviewer.strip().casefold()
                _require(canonical_reviewer.startswith("agent:"),
                         f"review[{index}].reviewer must use a canonical agent: id", errors)
                _require(canonical_reviewer not in reviewers, f"duplicate reviewer {reviewer}", errors)
                reviewers.add(canonical_reviewer)
            _require(review.get("source_check") == "original", f"review[{index}] must check original sources", errors)
            _require(review.get("disposition") == record.get("decision"),
                     f"review[{index}] must assent to the recorded decision", errors)
            receipt = review.get("receipt_url", "")
            parsed = urlparse(receipt) if isinstance(receipt, str) else None
            _require(bool(parsed and parsed.scheme == "https" and parsed.netloc == "github.com"
                          and GITHUB_RECEIPT.fullmatch(parsed.path + (f"#{parsed.fragment}" if parsed.fragment else ""))),
                     f"review[{index}] needs an attributable GitHub issue or PR comment receipt", errors)

    net_status = record.get("conservative_net_earnings_status")
    _require(isinstance(net_status, str) and net_status in ALLOWED_NET_STATES,
             "conservative_net_earnings_status must be positive, unknown or nonpositive", errors)

    if isinstance(gates, dict) and set(gates) == set(REQUIRED_GATES):
        statuses = [gates[name].get("status") for name in REQUIRED_GATES if isinstance(gates[name], dict)]
        if record.get("decision") == "PASS":
            _require(statuses == ["verified"] * len(REQUIRED_GATES),
                     "PASS requires every required gate to be verified", errors)
            _require(all(gates[name].get("chain_complete") is True for name in REQUIRED_GATES),
                     "PASS requires a complete evidence chain for every gate", errors)
            _require(record.get("conservative_net_earnings_status") == "positive",
                     "PASS requires positive conservative net earnings", errors)
        elif record.get("decision") == "NO_VERIFIABLE_ROUTE":
            _require(any(status != "verified" for status in statuses),
                     "NO_VERIFIABLE_ROUTE requires at least one unresolved or failed gate", errors)
            _require("not evidence of unavailability" in record.get("limitations", "").lower(),
                     "negative disposition must explicitly avoid an unavailability claim", errors)

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    args = parser.parse_args(argv)
    with args.record.open(encoding="utf-8") as handle:
        record = json.load(handle)
    errors = validate(record)
    print(json.dumps({"ok": not errors, "errors": errors, "decision": record.get("decision")}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
