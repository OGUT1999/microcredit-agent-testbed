#!/usr/bin/env python3
"""Validate a bounded paid-work channel qualification record.

This is an evidence sufficiency gate, not a market-access probe. It never logs in,
contacts a platform, spends money, or treats an unverified route as unavailable.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from quote_consistency import COSTS, amount, analyze

REQUIRED_GATES = ("current_access", "current_demand", "worker_eligibility", "spendable_payout")
ALLOWED_GATE_STATES = {"verified", "unverified", "failed"}
ALLOWED_DECISIONS = {"IN_REVIEW", "PASS", "NO_VERIFIABLE_ROUTE"}
ALLOWED_NET_STATES = {"positive", "unknown", "nonpositive"}
MAX_RECORD_BYTES = 1024 * 1024
GITHUB_RECEIPT = re.compile(
    r"^/[^/]+/[^/]+/(?:issues|pull)/[1-9][0-9]*(?:#issuecomment-[1-9][0-9]*|#discussion_r[1-9][0-9]*)$"
)


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def _url(value):
    """Malformed source text is a validation finding, never an exception echo."""
    if not isinstance(value, str):
        return None
    try:
        return urlparse(value)
    except ValueError:
        return None


def _member(value, choices):
    return isinstance(value, str) and value in choices


def payout_readiness(record: dict) -> dict:
    """Prospective PASS arithmetic only; supplied sources still need human review.

    Cash amounts are conservative lower bounds, all costs conservative upper
    bounds in the same explicitly confirmed unit. Points use the existing fixed
    conversion diagnostic, never an inferred currency or endpoint pairing.
    """
    errors: list[str] = []
    result = {"errors": errors, "net_cash_lower_bound": None,
              "human_earnings_established": False, "financial_authority": False}
    if not isinstance(record, dict):
        errors.append("record must be an object")
        return result
    data = record.get("payout_economics")
    if not isinstance(data, dict):
        errors.append("PASS requires payout_economics; a positive-net label is insufficient")
        return result
    gates = record.get("gates", {})
    gate = gates.get("spendable_payout", {}) if isinstance(gates, dict) else {}
    allowed = gate.get("source_ids", []) if isinstance(gate, dict) else []
    allowed = {s for s in allowed if isinstance(s, str)} if isinstance(allowed, list) else set()

    def refs(value, label):
        valid = (isinstance(value, list) and 1 <= len(value) <= 20
                 and all(isinstance(s, str) and s in allowed for s in value)
                 and len(set(value)) == len(value))
        _require(valid, label + " needs unique spendable_payout source_ids", errors)

    currency = data.get("currency")
    _require(isinstance(currency, str) and bool(currency.strip()), "payout currency required", errors)
    _require(data.get("currency_unit_confirmed") is True,
             "payout currency unit must be explicitly confirmed; no SLL/SLE normalization", errors)
    refs(data.get("currency_source_ids"), "currency confirmation")
    costs = data.get("costs")
    cost_refs = data.get("cost_source_ids")
    _require(isinstance(costs, dict) and set(costs) == set(COSTS),
             "payout needs all three conservative worker-borne cost upper bounds", errors)
    _require(isinstance(cost_refs, dict) and set(cost_refs) == set(COSTS),
             "payout needs source_ids for each worker-borne cost", errors)
    parsed_costs = []
    for name in COSTS:
        refs(cost_refs.get(name) if isinstance(cost_refs, dict) else None, name)
        try:
            parsed_costs.append(amount(costs.get(name) if isinstance(costs, dict) else None))
        except ValueError:
            errors.append(name + " upper bound unknown or invalid; never zero by default")
    basis = data.get("basis")
    gross = None
    refs(data.get("gross_source_ids"), "current task gross lower bound")
    demand = gates.get("current_demand", {}) if isinstance(gates, dict) else {}
    demand_refs = demand.get("source_ids", []) if isinstance(demand, dict) else []
    gross_refs = data.get("gross_source_ids", [])
    _require(isinstance(gross_refs, list) and isinstance(demand_refs, list)
             and any(isinstance(s, str) and s in demand_refs for s in gross_refs),
             "gross lower bound must share a source with current_demand", errors)
    if basis == "cash":
        try:
            gross = amount(data.get("gross_cash_min"))
        except ValueError:
            errors.append("gross_cash_min must be a nonnegative exact amount")
        _require("quotes" not in data and "task_points_min" not in data,
                 "cash basis cannot bypass a supplied points conversion", errors)
    elif basis == "points":
        diagnostic = analyze(data)
        _require(diagnostic["status"] == "QUOTE_ARITHMETIC_CONSISTENT",
                 "points payout requires QUOTE_ARITHMETIC_CONSISTENT: " + diagnostic["status"], errors)
        _require(data.get("fixed_conversion_confirmed") is True,
                 "points payout requires source-confirmed fixed conversion, not a hypothesis", errors)
        refs(data.get("conversion_source_ids"), "fixed conversion confirmation")
        quotes = data.get("quotes")
        if isinstance(quotes, list) and 2 <= len(quotes) <= 20:
            for quote in quotes:
                if isinstance(quote, dict):
                    refs(quote.get("source_ids"), "conversion quote")
                    _require(quote.get("currency") == currency,
                             "conversion quote currency must match payout unit exactly", errors)
        try:
            points = amount(data.get("task_points_min"))
            if diagnostic["status"] == "QUOTE_ARITHMETIC_CONSISTENT":
                # Intersection lower bound, not independently paired endpoints.
                rate = max(Fraction(q["low_cash_per_point"]) for q in diagnostic["rate_intervals"])
                gross = points * rate
        except ValueError:
            errors.append("task_points_min must be a nonnegative exact amount")
    else:
        errors.append("payout basis must be cash or points")
    if not errors and gross is not None:
        net = gross - sum(parsed_costs)
        result["net_cash_lower_bound"] = str(net)
        _require(net > 0, "PASS requires strictly positive same-unit conservative net cash", errors)
    return result


def validate(record: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return ["record must be an object"]
    _require(type(record.get("schema_version")) is int and record["schema_version"] == 1,
             "schema_version must be 1", errors)
    for field in ("candidate_id", "candidate_name", "country", "checked_at", "decision", "limitations", "next_trigger"):
        _require(isinstance(record.get(field), str) and bool(record[field].strip()), f"{field} is required", errors)
    _require(_member(record.get("decision"), ALLOWED_DECISIONS),
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
                _require(source_id not in source_ids, "duplicate source id", errors)
                source_ids.add(source_id)
            _require(source.get("kind") == "original", f"sources[{index}] must be original", errors)
            url = source.get("url", "")
            parsed = _url(url)
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
            _require(_member(gate.get("status"), ALLOWED_GATE_STATES), f"gate {gate_name} has invalid status", errors)
            _require(isinstance(gate.get("chain_complete"), bool),
                     f"gate {gate_name}.chain_complete must be boolean", errors)
            if _member(gate.get("status"), ALLOWED_GATE_STATES) and isinstance(gate.get("chain_complete"), bool):
                _require((gate["status"] == "verified") == gate["chain_complete"],
                         f"gate {gate_name} must be verified exactly when its evidence chain is complete", errors)
            refs = gate.get("source_ids")
            _require(isinstance(refs, list) and len(refs) >= 1, f"gate {gate_name} needs source_ids", errors)
            if isinstance(refs, list):
                for source_id in refs:
                    _require(isinstance(source_id, str) and source_id in source_ids,
                             f"gate {gate_name} references unknown source", errors)
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
                _require(canonical_reviewer not in reviewers, "duplicate reviewer", errors)
                reviewers.add(canonical_reviewer)
            _require(review.get("source_check") == "original", f"review[{index}] must check original sources", errors)
            _require(review.get("disposition") == record.get("decision"),
                     f"review[{index}] must assent to the recorded decision", errors)
            receipt = review.get("receipt_url", "")
            parsed = _url(receipt)
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
            _require(all(isinstance(gates[name], dict) and gates[name].get("chain_complete") is True
                         for name in REQUIRED_GATES),
                     "PASS requires a complete evidence chain for every gate", errors)
            _require(record.get("conservative_net_earnings_status") == "positive",
                     "PASS requires positive conservative net earnings", errors)
            errors.extend(payout_readiness(record)["errors"])
        elif record.get("decision") == "NO_VERIFIABLE_ROUTE":
            _require(any(status != "verified" for status in statuses),
                     "NO_VERIFIABLE_ROUTE requires at least one unresolved or failed gate", errors)
            limitations = record.get("limitations")
            _require(isinstance(limitations, str) and "not evidence of unavailability" in limitations.lower(),
                     "negative disposition must explicitly avoid an unavailability claim", errors)

    return errors


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON member")
        result[key] = value
    return result


def _finite_json(value):
    raise ValueError("nonstandard JSON number")


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        # argparse's usual error includes arbitrary user arguments and paths.
        raise ValueError("invalid command arguments")


def main(argv: list[str] | None = None) -> int:
    parser = _Parser(prog="qualification.py", description=__doc__)
    parser.add_argument("record", type=Path)
    decision = None
    try:
        args = parser.parse_args(argv)
        with args.record.open("rb") as handle:
            raw = handle.read(MAX_RECORD_BYTES + 1)
        if len(raw) > MAX_RECORD_BYTES:
            raise ValueError("record exceeds bounded input size")
        record = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object,
                            parse_constant=_finite_json)
        errors = validate(record)
        if isinstance(record, dict) and _member(record.get("decision"), ALLOWED_DECISIONS):
            decision = record["decision"]
    except (OSError, ValueError, UnicodeError, RecursionError):
        errors = ["record could not be read or parsed; valid unique-member JSON required"]
    print(json.dumps({"ok": not errors, "errors": errors, "decision": decision}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
