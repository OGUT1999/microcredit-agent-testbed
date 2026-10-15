#!/usr/bin/env python3
"""Offline individual-quote arithmetic, never an offer, funding or income finding."""
from fractions import Fraction
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.record_input import read_record

CASH = ("inference", "gas_and_transactions", "payment_and_conversion", "other")
NONCASH = ("allocated_setup_and_subscriptions", "other")
HOURS = ("delivery", "rework", "support_and_dispute")
NUMBER = re.compile(r"[0-9]{1,18}(?:\.[0-9]{1,12})?\Z")
READY = "QUOTE_ARITHMETIC_READY_FOR_REVIEW"


def _object(value, keys):
    if value is None:
        return {}
    if not isinstance(value, dict) or set(value) - set(keys):
        raise ValueError("invalid object")
    return value


def analyze(record):
    """Review supplied bounded estimates only; no source or agreement authentication.

    Explicit currencies and fee bases are mandatory. A pooled reward is not an
    individual's price. Unknown operands suppress all projected margin output.
    """
    gaps = []
    result = {"scope": "SUPPLIED_INDIVIDUAL_QUOTE_ARITHMETIC_ONLY",
              "gaps": gaps, "arithmetic": None, "offer_authorized": False,
              "funding_established": False, "settled_payment_established": False,
              "human_earnings_established": False,
              "poverty_reduction_established": False, "financial_authority": False}
    r = _object(record, ("currency", "price_scope", "cost_basis", "basis_evidence",
                        "price", "fees", "cash_costs", "worker_pay", "owner_hours",
                        "owner_hourly_rate", "noncash_costs",
                        "all_costs_and_effort_bounded", "owner_hours_exclude_worker_hours",
                        "worker_pay_excluded_from_other_costs"))
    currency = r.get("currency")
    if currency is None:
        gaps.append("currency_unknown")
    elif not isinstance(currency, str) or not currency.strip():
        raise ValueError("invalid currency")
    for field in ("price_scope", "cost_basis", "basis_evidence"):
        value = r.get(field)
        if value is None:
            gaps.append(field + "_unknown")
        elif not isinstance(value, str) or not value.strip():
            raise ValueError("invalid text")
    if r.get("price_scope") != "individual_gross":
        gaps.append("individual_gross_price_not_established")
    if r.get("cost_basis") not in ("bounded_estimate", "observed_same_scope"):
        gaps.append("cost_basis_not_established")
    for field in ("all_costs_and_effort_bounded", "owner_hours_exclude_worker_hours",
                  "worker_pay_excluded_from_other_costs"):
        value = r.get(field)
        if value is not None and type(value) is not bool:
            raise ValueError("invalid assertion")
        if value is not True:
            gaps.append(field + "_not_established")

    def number(value, field):
        if value is None:
            gaps.append(field + "_unknown")
            return None
        if type(value) not in (str, int) or not NUMBER.fullmatch(str(value)):
            raise ValueError("invalid bounded amount")
        return Fraction(str(value))

    def money(value, field):
        item = _object(value, ("amount", "currency"))
        unit = item.get("currency")
        if unit is not None and (not isinstance(unit, str) or not unit.strip()):
            raise ValueError("invalid currency")
        if unit is None or currency is None or unit != currency:
            gaps.append(field + "_currency_not_confirmed")
        return number(item.get("amount"), field)

    price = money(r.get("price"), "price")
    worker = money(r.get("worker_pay"), "worker_pay")
    rate = money(r.get("owner_hourly_rate"), "owner_hourly_rate")
    cash = _object(r.get("cash_costs"), CASH)
    noncash = _object(r.get("noncash_costs"), NONCASH)
    hours = _object(r.get("owner_hours"), HOURS)
    cash_values = [money(cash.get(k), "cash_" + k) for k in CASH]
    noncash_values = [money(noncash.get(k), "noncash_" + k) for k in NONCASH]
    hour_values = [number(hours.get(k), "hours_" + k) for k in HOURS]
    fees = _object(r.get("fees"), ("basis", "platform_bps", "evaluator_bps"))
    basis = fees.get("basis")
    if basis is not None and not isinstance(basis, str):
        raise ValueError("invalid fee basis")
    if basis != "gross_individual_price":
        gaps.append("fee_basis_not_established")
    bps = []
    for field in ("platform_bps", "evaluator_bps"):
        value = fees.get(field)
        if value is None:
            gaps.append(field + "_unknown")
        elif type(value) is not int or not 0 <= value <= 10000:
            raise ValueError("invalid basis points")
        else:
            bps.append(value)
    if len(bps) == 2 and sum(bps) > 10000:
        raise ValueError("fees exceed gross price")
    if all(v is not None for v in hour_values) and sum(hour_values) > 0 and rate == 0:
        gaps.append("positive_owner_time_has_no_positive_valuation")
    if gaps:
        result["gaps"] = sorted(set(gaps))
        return {**result, "status": "INCOMPLETE_QUOTE"}

    # W appears exactly once. Owner hours exclude hours bought through W.
    # All these operands are supplied estimates, not measured cash collections.
    projected = price * (1 - Fraction(sum(bps), 10000))
    cash_total, noncash_total = sum(cash_values), sum(noncash_values)
    owner_hours = sum(hour_values)
    labor = owner_hours * rate
    full_cost = cash_total + worker + labor + noncash_total
    n_cash = projected - cash_total - worker
    n_full = n_cash - labor - noncash_total
    half_cap = full_cost <= projected / 2
    result["arithmetic"] = {
        "projected_post_percentage_fees": str(projected),
        "cash_costs_excluding_worker_pay": str(cash_total), "worker_pay_once": str(worker),
        "owner_hours_bound": str(owner_hours), "priced_owner_labor": str(labor),
        "allocated_noncash_costs": str(noncash_total), "full_cost_including_worker_pay": str(full_cost),
        "projected_n_cash": str(n_cash), "projected_n_full": str(n_full),
        "meets_half_post_fee_proceeds_cost_bar": half_cap,
        "positive_projected_full_contribution": n_full > 0,
    }
    return {**result, "status": READY if n_full > 0 and half_cap else "ECONOMICS_NOT_MET"}


def main(argv=None):
    try:
        result = analyze(read_record(argv, prog="agent_job_quote.py", description=__doc__))
    except (OSError, ValueError, TypeError, UnicodeError, RecursionError):
        result = {"scope": "SUPPLIED_INDIVIDUAL_QUOTE_ARITHMETIC_ONLY",
                  "status": "INVALID_QUOTE", "gaps": ["invalid_bounded_quote"],
                  "arithmetic": None, "offer_authorized": False, "funding_established": False,
                  "settled_payment_established": False, "human_earnings_established": False,
                  "poverty_reduction_established": False, "financial_authority": False}
    # No supplied labels, source references, paths or exception text are emitted.
    # Numbers still require private handling: this is not an anonymizer.
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == READY else 2 if result["status"] == "INVALID_QUOTE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
