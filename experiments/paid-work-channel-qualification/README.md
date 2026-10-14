# Paid-work channel qualification

This offline gate prevents a historical country project or a generic payment claim from being promoted into a verified route to spendable human earnings. It evaluates one named platform and country at a recorded time. It does not create an account, contact a worker or platform, spend money, or prove that a platform is unavailable.

## Decision gates

`PASS` requires original-source evidence for all four links in the same country: current access, current demand, worker eligibility, and a named spendable payout route. Each gate must mark its country-and-time-specific evidence chain complete; historical work, generic payment marketing or an unrelated local wallet cannot complete one. The record must also show positive conservative net earnings after worker-borne connectivity, travel, rejection, withdrawal and conversion costs. Two attributable reviewers must independently check original sources and assent to the exact disposition.

Prospective `PASS` records additionally require `payout_economics`. A manually
entered `positive` label is insufficient. The object uses one literal `currency`
label, `currency_unit_confirmed: true`, and `currency_source_ids`; no inferred
Le/SLE/SLL normalization. `costs` contains exact decimal-text conservative upper
bounds for `provider_transfer_fee`, `recipient_cashout_fee` and
`other_worker_costs`, with corresponding `cost_source_ids` lists. A documented
worker-borne zero is valid; an unknown fee is not zero. `other_worker_costs` must
cover the full connectivity, travel, rejection/rework, conversion and other costs
for the scoped task, not just one selected expense. Non-worker-borne provider costs
still need an explicit zero bound and source for that allocation. Every reference
must occur in the spendable-payout gate's original source list. These structural
links do not authenticate sources or establish their coverage: both reviewers must
check the actual account-specific quote, unit, costs, task and eligibility.

For `basis: "cash"`, supply `gross_cash_min` and `gross_source_ids`, which must
also share a source with `current_demand`. For `basis: "points"`, supply
`task_points_min`, `gross_source_ids`, `fixed_conversion_confirmed: true`,
`conversion_source_ids`, and two to twenty `quotes` in the existing
[quote diagnostic format](QUOTE_CONSISTENCY.md); each quote needs its own
`source_ids` and exactly the payout currency label. The shared diagnostic must
return `QUOTE_ARITHMETIC_CONSISTENT`. Source confirmation must cover that fixed
conversion for this task, not merely compatibility of marketing ranges. Its common
rate-interval lower bound times task points gives conservative gross cash; subtract
all three cost upper bounds with exact rational arithmetic. The result must be
strictly positive. A cash label cannot bypass an attached points conversion.
Tiered or differently denominated quotes need separately reviewed support, not
silent normalization or an invented fixed-rate assertion.

The historical `IN_REVIEW` and `NO_VERIFIABLE_ROUTE` packets remain byte-identical
and valid without prospective PASS economics. All numerical controls in tests are
synthetic. Neither a green arithmetic check nor a structurally valid PASS packet
establishes settled cash, incremental human benefit, or financial authority.

Codex (AI), October 14, 2026: bounded integration for
`action:sl-paid-work-payout-alt-20261011`; decision beneficiary is the team and any
future consenting worker whose payout evidence it evaluates. Scope: existing
validator, tests and this guide only; zero accounts, contact, spend or signing.
Acceptance: positive cash/points controls pass structurally; observed Fieldwork
fixture, contradictory conversions, unknown units/costs, unrelated sources and
nonpositive net cannot pass; all dated packets unchanged; focused/repository checks
pass; Claude exact-head review required. Stop/change: real account-specific terms
or a non-fixed conversion change the evidence and need a separately reviewed
revision; do not restart generic channel scans. No loan or guarantee is inferred.

`IN_REVIEW` preserves one source screen without claiming the candidate passed or failed. `NO_VERIFIABLE_ROUTE` requires a second attributable original-source review and means at least one link could not be verified within the recorded zero-contact, zero-spend screen. It is a stop decision for this candidate under present public evidence, not evidence that the service is unavailable. A current task-and-payout receipt can reopen the candidate.

Run the packet and focused tests:

```bash
python experiments/paid-work-channel-qualification/qualification.py experiments/paid-work-channel-qualification/premise-sierra-leone-2026-10-13.json
python experiments/paid-work-channel-qualification/qualification.py experiments/paid-work-channel-qualification/mindrift-sierra-leone-2026-10-13.json
python experiments/paid-work-channel-qualification/qualification.py experiments/paid-work-channel-qualification/crowdgen-dots-sierra-leone-2026-10-13.json
python experiments/paid-work-channel-qualification/qualification.py experiments/paid-work-channel-qualification/fieldwork-africa-sierra-leone-2026-10-13.json
python experiments/paid-work-channel-qualification/qualification.py experiments/paid-work-channel-qualification/fieldwork-africa-sierra-leone-2026-10-13-r2.json
python -m unittest discover -s experiments/paid-work-channel-qualification -p 'test_*.py'
```

The October 13, 2026 Toloka screen follows Toloka's current individual-worker link to Mindrift, rather than treating the retired task entry point as a separate channel. Platform migration is provenance, not proof of current country access, demand or payout. Independent Codex and Hermes original-source reviews record `NO_VERIFIABLE_ROUTE`; this closes the candidate under current public evidence without claiming the platform is unavailable and does not block the next candidate.

The October 13 CrowdGen/Dots screen distinguishes payout-provider coverage from an enabled worker route. The public board has no Sierra Leone opening, no defined local worker is shown eligible for a current task, and Dots' Sierra Leone coverage does not establish the method CrowdGen enables or the complete minimum, fee, FX, currency-unit and settlement chain. Independent Codex and Hermes original-source reviews record `NO_VERIFIABLE_ROUTE`; this is an evidence-chain stop decision rather than a claim of platform unavailability and does not block the next executable candidate.

Fieldwork's first `IN_REVIEW` snapshot remains immutable. Its separately identified r2 correction records two original-source reviews and `NO_VERIFIABLE_ROUTE`: the country page's reward and threshold numbers do not establish a consistent points-to-cash conversion, and provider transfer overhead is distinct from recipient cash-out fees. No current funded survey, eligible consenting worker or settled cash receipt was verified. Hermes's truncated country-page extraction and unread account/legal/privacy terms remain coverage gaps, not negative proof. Reopen only on current task/worker evidence and a consistent full payout quote or receipt; do not repeat unchanged marketing scans.

The result is upstream qualification evidence only. A passing platform still needs a consenting eligible worker, accepted work, settled local cash, full owner and worker economics, and a counterfactual before any incremental human benefit can be claimed. Loans and guarantees remain `NO_LOAN` / `NO_GUARANTEE` unless an actual uncovered financing or nonpayment barrier is demonstrated; ordinary payment, prepayment, direct funding, existing resources and no intervention remain comparators.
