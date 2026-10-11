#!/usr/bin/env python3
"""Source-grounded external bounty qualification, zero outreach or transfers.

Crucial distinctions: an advertised bounty is not an assigned job, a claim is not
payment, a platform-reward listing is not a worker's real-asset shortfall, and a
public platform payout to somebody else is not this project's human benefit.
"""
import argparse
import json
from pathlib import Path


REWARD_STATES = {
    "platform_available_reward",
    "issuer_claim_only",
    "explicit_no_payment_promise",
}


def classify(row):
    assert row["reward_evidence"] in REWARD_STATES
    open_paid_ad = (row["state"] == "open" and row["source_issue_current_state"] == "open"
                    and row["advertised_usd"] > 0)
    platform_reward = (row["reward_evidence"] == "platform_available_reward"
                       and row["source_issue_current_state"] == "open")
    buyer_external = row["buyer_control"] == "external_repo_owner"
    funded_assignment = bool(
        open_paid_ad and platform_reward and buyer_external
        and row["assigned_worker_confirmed"]
        and row["payout_rail_verified_for_target_worker"]
    )
    human_first_job_ready = bool(
        funded_assignment and row["worker_skill_and_eligibility_verified"]
        and row["ai_assisted_work_permitted_by_buyer_verified"] is True
    )
    credit_qualified = bool(
        human_first_job_ready
        and row["mandatory_prepaid_input_known"] is True
        and row["worker_same_asset_shortfall_verified"]
        and row["prepayment_or_sponsorship_excluded"]
    )
    missing = []
    if not open_paid_ad:
        missing.append("no presently open source issue advertising paid work; stale or nonpaid listing")
    if not platform_reward:
        missing.append("available reward not verified on payment platform")
    if not row["assigned_worker_confirmed"]:
        missing.append("no independently accepted assignment to a worker")
    if not row["payout_rail_verified_for_target_worker"]:
        missing.append("target worker payout eligibility unverified")
    if not row["worker_skill_and_eligibility_verified"]:
        missing.append("suitable eligible worker not established")
    if row["ai_assisted_work_permitted_by_buyer_verified"] is not True:
        missing.append("buyer agent-assisted-work permission absent or unknown")
    if row["mandatory_prepaid_input_known"] is not True:
        missing.append("mandatory pre-delivery cost not established")
    if not row["worker_same_asset_shortfall_verified"]:
        missing.append("worker's asset-specific cash shortfall unverified")
    if not row["prepayment_or_sponsorship_excluded"]:
        missing.append("cheaper alternatives not excluded")
    return {
        "id": row["id"],
        "advertised_paid_task": open_paid_ad,
        "platform_available_reward_verified_on_open_source_issue": platform_reward,
        "independent_buyer_assignment_confirmed": funded_assignment,
        "human_first_job_ready": human_first_job_ready,
        "credit_qualified": credit_qualified,
        "missing_evidence": missing,
    }


def scenarios(gross_usd, hours=(5, 10, 20), pay_chances=(.2, .5, 1.0)):
    """Sensitivity scenarios, not estimated actual award probabilities."""
    return [
        {"gross_usd": gross_usd, "hypothetical_payment_probability": p,
         "hours": h, "hypothetical_expected_gross_hourly_usd": round(gross_usd*p/h, 3)}
        for h in hours for p in pay_chances
    ]


def report(data):
    rows = [classify(x) for x in data["candidates"]]
    return {
        "source_checked_date_utc": data["checked_date_utc"],
        "candidate_count": len(rows),
        "adverts_with_positive_amount": sum(r["advertised_paid_task"] for r in rows),
        "platform_available_rewards": sum(r["platform_available_reward_verified_on_open_source_issue"] for r in rows),
        "verified_assignments": sum(r["independent_buyer_assignment_confirmed"] for r in rows),
        "verified_first_job_ready": sum(r["human_first_job_ready"] for r in rows),
        "verified_credit_qualified": sum(r["credit_qualified"] for r in rows),
        "rows": rows,
    }


def run_tests(data):
    result = report(data)
    assert result["candidate_count"] == 7
    assert result["adverts_with_positive_amount"] == 4
    assert result["platform_available_rewards"] == 1
    assert result["verified_assignments"] == 0
    assert result["verified_first_job_ready"] == 0
    assert result["verified_credit_qualified"] == 0
    assert classify(data["candidates"][4])["advertised_paid_task"] is False
    assert classify(data["candidates"][3])["platform_available_reward_verified_on_open_source_issue"] is False
    assert classify(data["candidates"][5])["platform_available_reward_verified_on_open_source_issue"] is False
    assert classify(data["candidates"][6])["platform_available_reward_verified_on_open_source_issue"] is True
    assert data["candidates"][6]["ai_assisted_work_permitted_by_buyer_verified"] is False
    test_row = dict(data["candidates"][6])
    test_row.update(assigned_worker_confirmed=True, payout_rail_verified_for_target_worker=True,
                    worker_skill_and_eligibility_verified=True,
                    ai_assisted_work_permitted_by_buyer_verified=True)
    assert classify(test_row)["human_first_job_ready"] is True
    assert classify(test_row)["credit_qualified"] is False
    test_row.update(mandatory_prepaid_input_known=True,
                    worker_same_asset_shortfall_verified=True,
                    prepayment_or_sponsorship_excluded=True)
    assert classify(test_row)["credit_qualified"] is True
    test_row["reward_evidence"] = "issuer_claim_only"
    assert classify(test_row)["credit_qualified"] is False
    assert scenarios(50, (10,), (.5,))[0]["hypothetical_expected_gross_hourly_usd"] == 2.5
    print("PASS: 17 deterministic gate/economics assertions")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    default_data = Path(__file__).with_name("independent-bounty-candidates-2026-10-11.json")
    if not default_data.exists():  # standalone uninstalled bundle
        default_data = Path(__file__).with_name("northstar_external_bounty_candidates_2026-10-11.json")
    ap.add_argument("--data", type=Path, default=default_data)
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--sensitivities", action="store_true")
    args = ap.parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    if args.test:
        run_tests(data)
    else:
        out = report(data)
        if args.sensitivities:
            out["hypothetical_50_usd_award"] = scenarios(50)
        print(json.dumps(out, indent=2))
