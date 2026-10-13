"""Privacy-minimal application assistance gate. No personal or financial advice.

Only consumes applicant-authorized eligibility flags and aggregate costs. Never
stores name, address, contact, identity documents, or application credentials.
"""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Optional


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
    if x is None or isinstance(x, bool):
        return None
    try:
        value = Decimal(str(x))
    except (InvalidOperation, ValueError, TypeError):
        return None
    return value if value.is_finite() and value >= 0 else None


def first_day_cash_gap(outbound_fare, cash_before_first_employer_payment):
    """Provisional departure-date gap only; cannot establish financing necessity.

    Returns None if terms or actual costs are unknown. Does not count uncertain
    training/per-diem reimbursement as cash available before the trip.
    """
    fare = money(outbound_fare)
    cash = money(cash_before_first_employer_payment)
    if fare is None or cash is None:
        return None
    return max(fare - cash, Decimal(0))


def classify_assistance(e: Eligibility, fare=None, prepayment_cash=None,
                        employer_confirmed=False, actual_worker_cost_known=False):
    admission = application_gate(e)
    if admission != "ELIGIBLE_TO_CONSIDER_VOLUNTARY_APPLICATION":
        return {"admission": admission, "finance": "NO_LOAN_NO_GUARANTEE", "gap": None}
    gap = first_day_cash_gap(fare, prepayment_cash)
    if not employer_confirmed or not actual_worker_cost_known or gap is None:
        return {"admission": admission, "finance": "UNKNOWN_COSTS_NO_LOAN", "gap": None}
    if gap == 0:
        return {"admission": admission, "finance": "NO_LOAN_NO_GUARANTEE", "gap": "0"}
    return {"admission": admission,
            "finance": "VERIFY_EMPLOYER_PREPAY_OR_DIRECT_TICKET_BEFORE_ANY_SPONSORSHIP",
            "gap": str(gap)}
