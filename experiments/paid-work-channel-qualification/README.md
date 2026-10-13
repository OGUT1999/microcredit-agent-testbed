# Paid-work channel qualification

This offline gate prevents a historical country project or a generic payment claim from being promoted into a verified route to spendable human earnings. It evaluates one named platform and country at a recorded time. It does not create an account, contact a worker or platform, spend money, or prove that a platform is unavailable.

## Decision gates

`PASS` requires original-source evidence for all four links in the same country: current access, current demand, worker eligibility, and a named spendable payout route. Each gate must mark its country-and-time-specific evidence chain complete; historical work, generic payment marketing or an unrelated local wallet cannot complete one. The record must also show positive conservative net earnings after worker-borne connectivity, travel, rejection, withdrawal and conversion costs. Two attributable reviewers must independently check original sources and assent to the exact disposition.

`IN_REVIEW` preserves one source screen without claiming the candidate passed or failed. `NO_VERIFIABLE_ROUTE` requires a second attributable original-source review and means at least one link could not be verified within the recorded zero-contact, zero-spend screen. It is a stop decision for this candidate under present public evidence, not evidence that the service is unavailable. A current task-and-payout receipt can reopen the candidate.

Run the packet and focused tests:

```bash
python experiments/paid-work-channel-qualification/qualification.py experiments/paid-work-channel-qualification/premise-sierra-leone-2026-10-13.json
python experiments/paid-work-channel-qualification/qualification.py experiments/paid-work-channel-qualification/mindrift-sierra-leone-2026-10-13.json
python experiments/paid-work-channel-qualification/qualification.py experiments/paid-work-channel-qualification/crowdgen-dots-sierra-leone-2026-10-13.json
python experiments/paid-work-channel-qualification/qualification.py experiments/paid-work-channel-qualification/fieldwork-africa-sierra-leone-2026-10-13.json
python -m unittest discover -s experiments/paid-work-channel-qualification -p 'test_*.py'
```

The October 13, 2026 Toloka screen follows Toloka's current individual-worker link to Mindrift, rather than treating the retired task entry point as a separate channel. Platform migration is provenance, not proof of current country access, demand or payout. Independent Codex and Hermes original-source reviews record `NO_VERIFIABLE_ROUTE`; this closes the candidate under current public evidence without claiming the platform is unavailable and does not block the next candidate.

The October 13 CrowdGen/Dots screen distinguishes payout-provider coverage from an enabled worker route. The public board has no Sierra Leone opening, no defined local worker is shown eligible for a current task, and Dots' Sierra Leone coverage does not establish the method CrowdGen enables or the complete minimum, fee, FX, currency-unit and settlement chain. Independent Codex and Hermes original-source reviews record `NO_VERIFIABLE_ROUTE`; this is an evidence-chain stop decision rather than a claim of platform unavailability and does not block the next executable candidate.

The result is upstream qualification evidence only. A passing platform still needs a consenting eligible worker, accepted work, settled local cash, full owner and worker economics, and a counterfactual before any incremental human benefit can be claimed. Loans and guarantees remain `NO_LOAN` / `NO_GUARANTEE` unless an actual uncovered financing or nonpayment barrier is demonstrated; ordinary payment, prepayment, direct funding, existing resources and no intervention remain comparators.
