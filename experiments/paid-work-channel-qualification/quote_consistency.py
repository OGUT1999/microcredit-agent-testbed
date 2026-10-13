#!/usr/bin/env python3
"""Offline arithmetic diagnostic; never a channel PASS or an earnings claim."""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import re

NUMBER = re.compile(r"[0-9]{1,18}(?:\.[0-9]{1,12})?\Z")
COSTS = ("provider_transfer_fee", "recipient_cashout_fee", "other_worker_costs")


def amount(value):
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ValueError("amounts require nonnegative integer or exact decimal text")
    if not NUMBER.fullmatch(str(value)):
        raise ValueError("invalid or excessively large decimal amount")
    return Fraction(str(value))


def analyze(record):
    """Test one fixed linear conversion hypothesis, without pairing range endpoints.

    A points interval [p0,p1] and cash interval [c0,c1] permits only rates in
    [c0/p1,c1/p0]. Disjoint intervals cannot share a fixed same-unit rate.
    This does not disprove tiered pricing or establish what any worker receives.
    """
    errors, intervals = [], []
    result = {"scope": "offline_quote_arithmetic_only", "channel_pass": False,
              "human_earnings_established": False, "errors": errors,
              "hypothesis": "one fixed linear conversion in the same confirmed currency unit",
              "rate_intervals": intervals, "fixed_rate_compatible": None,
              "currency_confirmed": False, "full_worker_costs_known": False}
    if not isinstance(record, dict):
        errors.append("record must be an object")
        return {**result, "status": "INVALID_QUOTE"}
    quotes = record.get("quotes")
    if not isinstance(quotes, list) or not 2 <= len(quotes) <= 20:
        errors.append("two to twenty quote records required")
        return {**result, "status": "INVALID_QUOTE"}
    ids, currencies, bounds = set(), set(), []
    for q in quotes:
        try:
            if not isinstance(q, dict):
                raise ValueError("each quote must be an object")
            ident, currency = q.get("id"), q.get("currency")
            if not isinstance(ident, str) or not ident.strip() or ident in ids:
                raise ValueError("quote ids must be unique nonempty text")
            ids.add(ident)
            if not isinstance(currency, str) or not currency.strip():
                raise ValueError("currency label required; no implicit SLL/SLE conversion")
            currencies.add(currency)
            p0, p1 = amount(q.get("points_min")), amount(q.get("points_max"))
            c0, c1 = amount(q.get("cash_min")), amount(q.get("cash_max"))
            if p0 <= 0 or p1 < p0 or c1 < c0:
                raise ValueError("positive ordered point bounds and ordered cash bounds required")
            low, high = c0 / p1, c1 / p0
            bounds.append((low, high))
            intervals.append({"id": ident, "currency": currency,
                              "low_cash_per_point": str(low), "high_cash_per_point": str(high)})
        except ValueError as error:
            errors.append(str(error))
    costs = record.get("costs", {})
    if not isinstance(costs, dict):
        errors.append("costs must be an object")
    else:
        for name in COSTS:
            if costs.get(name) is not None:
                try:
                    amount(costs[name])
                except ValueError as error:
                    errors.append(name + ": " + str(error))
        result["full_worker_costs_known"] = all(costs.get(n) is not None for n in COSTS)
    if errors:
        result["full_worker_costs_known"] = False
        return {**result, "status": "INVALID_QUOTE"}
    # Different currency labels are not merged, even if one is a legacy code.
    same_label = len(currencies) == 1
    if same_label:
        result["fixed_rate_compatible"] = max(b[0] for b in bounds) <= min(b[1] for b in bounds)
    confirmed = same_label and record.get("currency_unit_confirmed") is True
    result["currency_confirmed"] = confirmed
    if not confirmed:
        status = "INCOMPLETE_QUOTE"
    elif result["fixed_rate_compatible"] is False:
        status = "INCONSISTENT_QUOTE"
    elif not result["full_worker_costs_known"]:
        status = "INCOMPLETE_QUOTE"
    else:
        status = "QUOTE_ARITHMETIC_CONSISTENT"
    result["interpretation"] = (
        "Rate compatibility assumes one same-unit fixed conversion; it does not certify source claims, "
        "task access, eligibility, settlement, net income, benefit or financing necessity. "
        "Transfer overhead and recipient cash-out costs are separate. Unknown costs are not zero."
    )
    return {**result, "status": status}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    try:
        result = analyze(json.loads(args.record.read_text(encoding="utf-8")))
    except (OSError, ValueError) as error:
        result = {"status": "INVALID_QUOTE", "errors": [str(error)], "channel_pass": False}
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "QUOTE_ARITHMETIC_CONSISTENT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
