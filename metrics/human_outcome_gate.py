#!/usr/bin/env python3
"""Offline supplied-evidence readiness, never truth verification or impact inference.

No network, custody, transactions, financing recommendation, or poverty estimate.
Missing evidence is NOT_ESTABLISHED. A complete packet is READY_FOR_REVIEW only.
Amounts are nonnegative decimal strings or integers, never binary floats.
"""
from datetime import date, datetime
from decimal import Decimal, DecimalException, InvalidOperation
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.record_input import read_record


COST_CATEGORIES = (
    "payout_fees", "work_expenses", "worker_contributions", "taxes",
    "allocated_setup_and_subscriptions", "other",
)
READY = "READY_FOR_REVIEW"
UNKNOWN = "NOT_ESTABLISHED"


def _object(value, keys, path, gaps):
    if value is None:
        gaps.append(path + ": missing")
        return {}
    if not isinstance(value, dict):
        raise ValueError(path + ": expected object")
    extra = set(value) - set(keys)
    if extra:
        raise ValueError(path + ": unsupported fields " + ", ".join(sorted(extra)))
    return value


def _text(obj, key, path, gaps):
    value = obj.get(key)
    if value is None:
        gaps.append(path + "." + key + ": missing")
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(path + "." + key + ": expected nonempty string")
    return value


def _true(obj, key, path, gaps):
    value = obj.get(key)
    if value is not None and type(value) is not bool:
        raise ValueError(path + "." + key + ": expected boolean")
    if value is not True:
        gaps.append(path + "." + key + ": not established")


def _amount(obj, key, path, gaps):
    value = obj.get(key)
    if value is None:
        gaps.append(path + "." + key + ": unknown")
        return None
    if type(value) not in (str, int):
        raise ValueError(path + "." + key + ": use decimal string or integer")
    try:
        result = Decimal(value)
    except InvalidOperation as error:
        raise ValueError(path + "." + key + ": invalid decimal") from error
    if not result.is_finite() or result < 0:
        raise ValueError(path + "." + key + ": expected finite nonnegative amount")
    return result


def _date(obj, key, path, gaps):
    value = _text(obj, key, path, gaps)
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(path + "." + key + ": expected ISO calendar date") from error


def _reference(value, path, gaps):
    ref = _object(value, ("source", "observed_at"), path, gaps)
    _text(ref, "source", path, gaps)
    stamp = _text(ref, "observed_at", path, gaps)
    if stamp is not None:
        try:
            parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        except ValueError as error:
            raise ValueError(path + ": invalid observed_at") from error
        if parsed.tzinfo is None:
            raise ValueError(path + ": observed_at must include timezone")


def _strings(obj, key, path, gaps):
    value = obj.get(key)
    if value is None or value == []:
        gaps.append(path + "." + key + ": missing")
    elif not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise ValueError(path + "." + key + ": expected nonempty strings")


def _stage(gaps):
    return {"state": UNKNOWN if gaps else READY, "gaps": sorted(set(gaps))}


def classify(packet):
    """Classify completeness of reported records; assertions are not authenticated.

    Even READY_FOR_REVIEW does not establish earnings, incrementality, poverty
    reduction, consent validity, legal eligibility, or sponsor/pool sustainability.
    Identifiers should be pseudonymous; never publish consented personal records.
    """
    common = []
    packet = _object(packet, ("context", "job", "baseline", "followup",
                             "poverty_line", "counterfactual", "harms"), "packet", common)
    context = _object(packet.get("context"), ("locality", "local_currency"), "context", common)
    locality = _text(context, "locality", "context", common)
    currency = _text(context, "local_currency", "context", common)
    earnings = common.copy()
    job = _object(packet.get("job"), ("id", "worker_id", "client_id", "household_id", "evidence_kind",
                  "independent_client", "useful_work_accepted", "consent", "acceptance_evidence",
                  "client_independence_evidence", "consent_evidence",
                  "payout", "worker_costs", "time_hours", "time_evidence"), "job", earnings)
    for key in ("id", "worker_id", "client_id"):
        _text(job, key, "job", earnings)
    # Individual wage evidence does not justify collecting household linkage.
    # Require that link only when reviewing the household/poverty stages below.
    if job.get("household_id") is not None:
        _text(job, "household_id", "job", earnings)
    if job.get("client_id") and job.get("client_id") == job.get("worker_id"):
        earnings.append("job: same client/worker identifier is not independent commerce")
    if _text(job, "evidence_kind", "job", earnings) != "observed_real_value":
        earnings.append("job: only observed real-value records qualify; models/testnet are excluded")
    for key in ("independent_client", "useful_work_accepted", "consent"):
        _true(job, key, "job", earnings)
    _reference(job.get("acceptance_evidence"), "job.acceptance_evidence", earnings)
    _reference(job.get("client_independence_evidence"), "job.client_independence_evidence", earnings)
    _reference(job.get("consent_evidence"), "job.consent_evidence", earnings)
    payout = _object(job.get("payout"), ("kind", "amount", "currency", "settled",
                     "spendable_locally", "evidence"), "payout", earnings)
    if _text(payout, "kind", "payout", earnings) != "earned_wage":
        earnings.append("payout: only separately identified earned wage; principal/reimbursements excluded")
    received = _amount(payout, "amount", "payout", earnings)
    if _text(payout, "currency", "payout", earnings) != currency:
        earnings.append("payout: local settled currency mismatch")
    for key in ("settled", "spendable_locally"):
        _true(payout, key, "payout", earnings)
    _reference(payout.get("evidence"), "payout.evidence", earnings)
    costs = _object(job.get("worker_costs"), COST_CATEGORIES, "worker_costs", earnings)
    already_deducted = Decimal(0)
    additional_costs = Decimal(0)
    for key in COST_CATEGORIES:
        entry = _object(costs.get(key), ("amount", "currency", "evidence", "already_deducted_from_payout"), "costs." + key, earnings)
        amount = _amount(entry, "amount", "costs." + key, earnings)
        deducted = entry.get("already_deducted_from_payout")
        if deducted is None:
            earnings.append("costs." + key + ": already_deducted_from_payout unknown")
        elif type(deducted) is not bool:
            raise ValueError("costs." + key + ": already_deducted_from_payout must be boolean")
        elif amount is not None:
            if deducted:
                already_deducted += amount
            else:
                additional_costs += amount
        if _text(entry, "currency", "costs." + key, earnings) != currency:
            earnings.append("costs." + key + ": local currency mismatch")
        _reference(entry.get("evidence"), "costs." + key + ".evidence", earnings)
    _amount(job, "time_hours", "job", earnings)
    _reference(job.get("time_evidence"), "job.time_evidence", earnings)

    welfare = common.copy()
    rows = []
    welfare_keys = ("household_id", "population_scope", "measure", "unit", "currency", "price_basis", "amount",
                    "period_start", "period_end", "household_size", "person_days",
                    "household_size_evidence", "evidence")
    for label in ("baseline", "followup"):
        row = _object(packet.get(label), welfare_keys, label, welfare)
        rows.append(row)
        for key in ("household_id", "measure", "unit", "currency", "price_basis"):
            _text(row, key, label, welfare)
        if _text(row, "population_scope", label, welfare) != "whole_household":
            welfare.append(label + ": whole-household welfare required; worker wage is insufficient")
        if not job.get("household_id") or row.get("household_id") != job.get("household_id"):
            welfare.append(label + ": household not linked to worker")
        if row.get("measure") not in ("consumption", "income"):
            welfare.append(label + ": household consumption or household income measure required")
        if row.get("unit") != "local_currency_per_person_day" or row.get("currency") != currency:
            welfare.append(label + ": local per-person-day unit/currency required; FX/PPP proxy excluded")
        if not re.fullmatch(r"local_constant_[0-9]{4}", row.get("price_basis") or ""):
            welfare.append(label + ": explicit local constant-price reference year required")
        _amount(row, "amount", label, welfare)
        start = _date(row, "period_start", label, welfare)
        end = _date(row, "period_end", label, welfare)
        size = row.get("household_size")
        if size is None:
            welfare.append(label + ": household size unknown")
        elif type(size) is not int or size < 1:
            raise ValueError(label + ": household_size must be positive integer")
        person_days = _amount(row, "person_days", label, welfare)
        if start and end:
            days = (end - start).days + 1
            if days <= 0:
                raise ValueError(label + ": reversed period")
            if size is not None and person_days is not None and person_days != size * days:
                welfare.append(label + ": person-days inconsistent with reported constant household size/period")
        _reference(row.get("household_size_evidence"), label + ".household_size_evidence", welfare)
        _reference(row.get("evidence"), label + ".evidence", welfare)
    for key in ("household_id", "measure", "unit", "currency", "price_basis"):
        if rows[0].get(key) != rows[1].get(key):
            welfare.append("baseline/followup: " + key + " mismatch")
    baseline_end = _date(rows[0], "period_end", "baseline", [])
    followup_start = _date(rows[1], "period_start", "followup", [])
    if baseline_end and followup_start and followup_start <= baseline_end:
        welfare.append("baseline/followup: periods overlap or chronology reversed")

    impact = earnings + welfare
    line = _object(packet.get("poverty_line"), ("kind", "authority", "locality", "measure", "unit",
                   "currency", "price_basis", "amount", "valid_from", "valid_to", "evidence"), "poverty_line", impact)
    if _text(line, "kind", "poverty_line", impact) != "authoritative_local":
        impact.append("poverty_line: authoritative local line required; USD FX is not 2021 PPP")
    _text(line, "authority", "poverty_line", impact)
    if _text(line, "locality", "poverty_line", impact) != locality:
        impact.append("poverty_line: jurisdiction mismatch")
    for key in ("measure", "unit", "currency", "price_basis"):
        _text(line, key, "poverty_line", impact)
        if line.get(key) != rows[0].get(key) or line.get(key) != rows[1].get(key):
            impact.append("poverty_line: " + key + " incompatible with household welfare")
    threshold = _amount(line, "amount", "poverty_line", impact)
    if threshold == 0:
        impact.append("poverty_line: positive threshold required")
    valid_from = _date(line, "valid_from", "poverty_line", impact)
    valid_to = _date(line, "valid_to", "poverty_line", impact)
    if valid_from and valid_to and valid_from > valid_to:
        raise ValueError("poverty_line: reversed validity dates")
    for label, row in zip(("baseline", "followup"), rows):
        start = _date(row, "period_start", label, [])
        end = _date(row, "period_end", label, [])
        if valid_from and valid_to and start and end and not (valid_from <= start <= end <= valid_to):
            impact.append("poverty_line: validity does not cover " + label)
    _reference(line.get("evidence"), "poverty_line.evidence", impact)
    counter = _object(packet.get("counterfactual"), ("design", "outcome_unit", "assignment_unit", "estimand", "assumptions",
                      "limitations", "protocol", "comparison_evidence", "credible_basis"), "counterfactual", impact)
    design = _text(counter, "design", "counterfactual", impact)
    if design not in ("randomized_comparison", "quasi_experimental_comparison"):
        impact.append("counterfactual: explicit comparison design required; before/after alone insufficient")
    if _text(counter, "outcome_unit", "counterfactual", impact) != "household":
        impact.append("counterfactual: household outcome unit required")
    assignment = _text(counter, "assignment_unit", "counterfactual", impact)
    if assignment not in ("household", "worker", "noncompeting_job", "client", "community"):
        impact.append("counterfactual: eligible assignment unit required; competing applications cannot separate displacement")
    _text(counter, "estimand", "counterfactual", impact)
    for key in ("assumptions", "limitations"):
        _strings(counter, key, "counterfactual", impact)
    for key in ("protocol", "comparison_evidence", "credible_basis"):
        _reference(counter.get(key), "counterfactual." + key, impact)
    harms = _object(packet.get("harms"), ("displacement", "worker_welfare", "costs_and_time",
                    "adverse_events"), "harms", impact)
    for key in ("displacement", "worker_welfare", "costs_and_time", "adverse_events"):
        _reference(harms.get(key), "harms." + key, impact)
    result = {
        "scope": "SUPPLIED_PACKET_READINESS_ONLY; no authentication, causal inference or poverty finding",
        "earned_income_packet": _stage(earnings),
        "household_comparison_packet": _stage(welfare),
        "poverty_impact_evaluation_packet": _stage(impact),
    }
    if not earnings:
        result["reported_earnings_arithmetic"] = {
            "label": "Reported settled earned cash received minus additional worker cash costs; NOT verified or incremental earnings",
            "currency": currency, "settled_wage_received": str(received),
            "worker_costs_already_deducted": str(already_deducted),
            "additional_worker_cash_costs": str(additional_costs),
            "net_cash": str(received - additional_costs),
        }
    return result


def main(argv=None):
    try:
        report = classify(read_record(argv, prog="human_outcome_gate.py",
                                      description=__doc__, argument_name="packet"))
    except (OSError, ValueError, TypeError, UnicodeError, RecursionError, DecimalException):
        report = {"scope": "SUPPLIED_PACKET_READINESS_ONLY; no authentication, causal inference or poverty finding",
                  "status": "INVALID_PACKET",
                  "errors": ["packet could not be read, parsed or classified; bounded unique-member JSON required"],
                  "human_earnings_established": False, "poverty_reduction_established": False,
                  "financial_authority": False}
        print(json.dumps(report, indent=2))
        return 2
    # The API retains the reported unit for private review. CLI diagnostics must
    # not repeat arbitrary supplied labels; amounts still require private handling.
    if "reported_earnings_arithmetic" in report:
        del report["reported_earnings_arithmetic"]["currency"]
        report["reported_earnings_arithmetic"]["currency_label_omitted"] = True
    report.update(human_earnings_established=False, poverty_reduction_established=False,
                  financial_authority=False)
    print(json.dumps(report, indent=2))
    return 0  # Parsing success only; consumers must read each readiness state.


if __name__ == "__main__":
    raise SystemExit(main())
