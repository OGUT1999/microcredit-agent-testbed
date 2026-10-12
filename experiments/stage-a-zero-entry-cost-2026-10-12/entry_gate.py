"""No-contact, no-spend qualification of Upwork entry paths, 2026-10-12.

This is a rules/route diagnostic, NOT a signed-in API verification, payment, job post,
contract, application, worker recruitment or legal/compliance determination.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class Path(Enum):
    OPEN_PROPOSAL = 'open_proposal'
    CLIENT_INVITATION = 'client_invitation'
    DIRECT_OFFER = 'direct_offer'
    DIRECT_CONTRACT = 'direct_contract'

@dataclass(frozen=True)
class Candidate:
    path: Path
    # All defaults fail closed: do not turn unknown into false expense or permission.
    actual_platform_event: bool = False
    worker_upwork_account: Optional[bool] = None
    preexisting_client_relationship: bool = False
    free_connects_suffice: Optional[bool] = None
    buyer_genuinely_needs_work: bool = False
    price_and_acceptance_frozen: bool = False
    inside_upwork_until_contract: bool = False
    worker_pays_to_enter: Optional[bool] = None
    required_identity_or_badge_has_cash_cost: Optional[bool] = None
    worker_verified_payout: bool = False
    worker_consented: bool = False
    actual_fees_verified: bool = False
    actual_client_payment_terms_verified: bool = False
    operator_authorized: bool = False
    feedback_or_rating_is_undue_incentive: bool = False


def assess(c: Candidate):
    reasons = []
    # Structural screening: we have original-source support for the *mechanism*,
    # not proof that any particular worker or account has executed it.
    if c.path == Path.OPEN_PROPOSAL:
        if c.worker_upwork_account is not True:
            reasons.append('UPWORK_ACCOUNT_NOT_CONFIRMED')
        if c.free_connects_suffice is not True:
            reasons.append('PROPOSAL_CONNECTS_COST_NOT_ELIMINATED')
    elif c.path == Path.CLIENT_INVITATION:
        if c.worker_upwork_account is not True:
            reasons.append('UPWORK_ACCOUNT_NOT_CONFIRMED')
        # Upwork: replying to a client-initiated invitation costs zero Connects.
        # No claim about how expensive the worker's onboarding is.
    elif c.path == Path.DIRECT_OFFER:
        if c.worker_upwork_account is not True:
            reasons.append('UPWORK_ACCOUNT_NOT_CONFIRMED')
        # Upwork: offer skips proposal; actual offer event required below.
    elif c.path == Path.DIRECT_CONTRACT:
        if c.worker_upwork_account is not False:
            reasons.append('DIRECT_CONTRACT_REQUIRES_NO_PRIOR_UPWORK_ACCOUNT')
        if not c.preexisting_client_relationship:
            reasons.append('DIRECT_CONTRACT_REQUIRES_PREEXISTING_RELATIONSHIP')
        # Upwork says this product does not include payment protection/disputes.
        reasons.append('DIRECT_CONTRACT_LACKS_PLATFORM_PAYMENT_PROTECTION')
    else:
        raise ValueError('unknown path')
    if not c.actual_platform_event:
        reasons.append('NO_ACTUAL_INVITE_OFFER_OR_APPLICATION')
    if not c.buyer_genuinely_needs_work:
        reasons.append('NO_VERIFIED_GENUINE_PURCHASE_USE')
    if not c.price_and_acceptance_frozen:
        reasons.append('SCOPE_OR_RUBRIC_NOT_FROZEN')
    if not c.inside_upwork_until_contract:
        reasons.append('PRECONTRACT_CHANNEL_NOT_VERIFIED')
    if c.worker_pays_to_enter is not False:
        reasons.append('ZERO_UPFRONT_WORKER_CASH_NOT_VERIFIED')
    # A zero-Connects proposal path does not guarantee free KYC/badge eligibility.
    # For restricted jobs, Upwork may require a 35-Connects verified badge.
    if c.required_identity_or_badge_has_cash_cost is not False:
        reasons.append('PAID_IDENTITY_OR_BADGE_BARRIER_NOT_EXCLUDED')
    if not c.worker_verified_payout:
        reasons.append('WORKER_PAYOUT_NOT_VERIFIED')
    if not c.worker_consented:
        reasons.append('NO_WORKER_CONSENT')
    if not c.actual_fees_verified:
        reasons.append('LIVE_FEES_UNKNOWN')
    if not c.actual_client_payment_terms_verified:
        reasons.append('CLIENT_PAYMENT_TERMS_NOT_VERIFIED')
    if c.feedback_or_rating_is_undue_incentive:
        reasons.append('FEEDBACK_BUILDING_RISK')
    if not c.operator_authorized:
        reasons.append('NO_AUTHORIZED_RECRUITMENT_OR_SPENDING')
    return {
        'route': c.path.value,
        'path_zero_connects_supported_by_primary_source': c.path in (Path.CLIENT_INVITATION, Path.DIRECT_OFFER),
        'ready_for_real_participant_or_spending': not reasons,
        'reasons': reasons,
        'observed_external_participants': 0,
        'verified_project_attributable_worker_earnings_usd': '0.00',
    }


if __name__ == '__main__':
    from json import dumps
    print(dumps([assess(Candidate(p)) for p in Path], indent=2))
