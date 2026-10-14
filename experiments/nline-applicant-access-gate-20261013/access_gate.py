"""Privacy-minimal application assistance gate. No personal or financial advice.

Only consumes applicant-authorized eligibility flags and aggregate costs. Never
stores name, address, contact, identity documents, or application credentials.
"""
from dataclasses import dataclass
from decimal import (Context, Decimal, DecimalException, Inexact, InvalidOperation,
                     Rounded, ROUND_HALF_EVEN)
from typing import Optional


# Same magnitude/scale bounds as the existing human-outcome cash gate. This
# in-memory API retains Decimal/int/float inputs and Decimal output; importing
# that gate's private Fraction parser would change its contract and diagnostics.
MAX_INTEGER_DIGITS = 32
MAX_FRACTIONAL_DIGITS = 12
MAX_AMOUNT_TEXT = 96


def _cash_context():
    # Fresh, explicit context: never inherit caller precision, traps or flags.
    return Context(prec=MAX_INTEGER_DIGITS + MAX_FRACTIONAL_DIGITS,
                   rounding=ROUND_HALF_EVEN, Emin=-MAX_FRACTIONAL_DIGITS,
                   Emax=MAX_INTEGER_DIGITS - 1, capitals=1, clamp=0, flags=[],
                   traps=[InvalidOperation, Inexact, Rounded])


@dataclass(frozen=True)
class Eligibility:
    consent: bool
    advertised_residency: Optional[bool]
    suitable_android: Optional[bool]
    advertised_languages: Optional[bool]
    employer_application_open: Optional[bool]
    cv_ready: Optional[bool] = None
    cover_letter_ready: Optional[bool] = None
    available_for_full_training_and_fieldwork: Optional[bool] = None


def application_gate(e: Eligibility) -> str:
    if e.consent is not True:
        return "NO_CONTACT_NO_APPLICATION"
    vals = (e.advertised_residency, e.suitable_android,
            e.advertised_languages, e.employer_application_open,
            e.cv_ready, e.cover_letter_ready,
            e.available_for_full_training_and_fieldwork)
    if any(v is False for v in vals):
        return "DO_NOT_SUGGEST_APPLICATION"
    if any(v is not True for v in vals):
        return "VERIFY_ELIGIBILITY_OR_OPEN_STATUS"
    return "ELIGIBLE_TO_CONSIDER_VOLUNTARY_APPLICATION"


def money(x):
    if type(x) not in (str, int, float, Decimal):
        return None
    if type(x) is int and (x < 0 or x >= 10 ** MAX_INTEGER_DIGITS):
        return None
    if type(x) is str and len(x) > MAX_AMOUNT_TEXT:
        return None
    try:
        value = x if type(x) is Decimal else Decimal(str(x), context=_cash_context())
    except (DecimalException, ValueError, TypeError):
        return None
    if not value.is_finite() or value < 0:
        return None
    _, digits, exponent = value.as_tuple()
    if (len(digits) > MAX_INTEGER_DIGITS + MAX_FRACTIONAL_DIGITS
            or exponent < -MAX_FRACTIONAL_DIGITS
            or exponent > MAX_INTEGER_DIGITS - 1
            or value.adjusted() >= MAX_INTEGER_DIGITS):
        return None
    return value


def first_day_cash_gap(outbound_fare, cash_before_first_employer_payment):
    """Provisional departure-date gap only; cannot establish financing necessity.

    Same-unit amounts only; no currency conversion is inferred. Returns None
    for unknown/invalid amounts or unsupported magnitude/scale. Does not count uncertain
    training/per-diem reimbursement as cash available before the trip.
    """
    fare = money(outbound_fare)
    cash = money(cash_before_first_employer_payment)
    if fare is None or cash is None:
        return None
    return max(_cash_context().subtract(fare, cash), Decimal(0))


def classify_assistance(e: Eligibility, fare=None, prepayment_cash=None,
                        employer_confirmed=False, actual_worker_cost_known=False):
    admission = application_gate(e)
    if admission != "ELIGIBLE_TO_CONSIDER_VOLUNTARY_APPLICATION":
        return {"admission": admission, "finance": "NO_LOAN_NO_GUARANTEE", "gap": None}
    gap = first_day_cash_gap(fare, prepayment_cash)
    if employer_confirmed is not True or actual_worker_cost_known is not True or gap is None:
        return {"admission": admission, "finance": "UNKNOWN_COSTS_NO_LOAN", "gap": None}
    if gap == 0:
        return {"admission": admission, "finance": "NO_LOAN_NO_GUARANTEE", "gap": "0"}
    return {"admission": admission,
            "finance": "VERIFY_EMPLOYER_PREPAY_OR_DIRECT_TICKET_BEFORE_ANY_SPONSORSHIP",
            "gap": str(gap)}
