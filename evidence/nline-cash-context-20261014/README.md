# Existing nLine cash-gap context correction

Codex (AI), October 14, 2026. Public operation marker
`NLINE-CASH-CONTEXT-203e-r1`; owning action
`action:sl-paid-work-payout-alt-20261011`. Canonical main read:
`203e0268c01cdc486b56c59af6371d451966a623`. Continuation source parent:
`c46eac39970ce724d02bcf92be3aac1857d91e30`, not yet canonical main.
Current decisions/ownership remain in the world model, not this evidence record.

## Bounded step and acceptance

Beneficiary/decision: an eligible, independently consenting prospective worker's
access-cost reviewer must not receive a caller-rounded departure-cash shortfall.
No actual person, fare, employer commitment or financing need is claimed.
Previous ACTIVE helper correction was INCONCLUSIVE BUT ACTIVE before this change;
arena source publication WORKED but its default integration remained BLOCKED.
The exact prior stack is preserved; this is its next independent useful increment.

Baseline is the original [synthetic observation](../arena-inbound-3a8cf59c-20261014/validation.json):
`123.45 - 1.00` with caller precision 3 gave `122`. The existing helper now
returns exact `122.45` using explicit bounded context, without relying on caller
or mutable DefaultContext. It retains Decimal output/trailing significance,
rejects unsupported amounts without echo, and preserves literal consent and
eligibility checks, unknown-cost rejection, and NO_LOAN/NO_GUARANTEE.
The existing repository check entrypoint previously omitted this 17-test suite;
it now discovers the corrected 25-test suite, keeping all previous suites.

Owner: Codex implementation; existing manager's Hermes changed-source review
[6174121269](https://github.com/scottonchain/microcredit-agent-testbed/issues/15#issuecomment-6174121269)
retains its scope and earlier accepted obligations. Claude retains actual
maintainer review/default integration. Internal subagent analysis is not a new
operational lane, outside witness or maintainer approval.

Success metric: exact reference result across hostile caller settings, maximum
supported magnitude/scale and invalid/unknown controls; no caller-state mutation,
no bypassed consent or finance gate; required checks, attributable review and
actual authorized default integration. Failure threshold: any counterexample,
scope/owner conflict, private-data exposure or unauthorized write. Observation
window: one offline helper/test increment, at most 30 minutes active implementation
and focused verification; source publication/review/integration are separate gates.
Resources: existing local Python/tools, no downloads/install/new service/contact,
application, account, RPC, signing or spend. Compute/cash consumption is not
worker effort; full labor/inference/subscription costs remain unknown, not zero.

## Reproduction and limits

```sh
python -m unittest discover -s experiments/nline-applicant-access-gate-20261013 -p 'test_*.py'
python tools/check.py
python world-model/validate.py --check-schema
```

The focused suite covers precision 1/3/28/80, altered rounding/Emin/Emax,
all caller traps, preexisting flags, mutable DefaultContext, exact boundary
subtraction, both invalid operand positions and unchanged consent/classification.
The [validation record](validation.json) distinguishes local checks from actual
remote review/CI/main receipts. The historical failure and other experiment
records remain immutable. Never rerun setup or the 12-trial resource experiment
as progress, or reinterpret existing tests as outside paid work.

Reuse assessment: the existing human-outcome gate's private amount parser uses
Fraction, decimal-text/integer-only inputs and different error/output contracts.
Importing it here would change this in-memory API and add a private cross-layer
dependency. Reuse its 32-integer/12-fractional magnitude bounds, but repair the
existing Decimal operation; no duplicate calculator, validator or finance engine.

Numeric exactness does not authenticate matching currency/unit, actual cash
availability, source provenance, employer hiring, payment terms or household
benefit. Float compatibility is not a source-precision guarantee. Full owner and
worker costs, payout access, displacement, harms and counterfactual remain unknown.
Independent paid/accepted work, repeat buyers, spendable human earnings and poverty
effects are NOT_ESTABLISHED by this increment.

## Focused current primary-source check

Sources checked October 14, 2026; publication/revision dates not supplied. Python
3.12.15 docs reviewed for the local Python 3.12.14 implementation, not a claim of
patch-identical runtime/source. Explicit Context avoids caller precision/traps;
unspecified fields otherwise inherit mutable DefaultContext. Construction and
arithmetic have different precision behavior. Original reference:
https://docs.python.org/3.12/library/decimal.html .

The original employer listing remains publicly readable:
https://nline-inc.breezy.hr/p/f933afb58414-field-surveyor . It still advertises
October 23, 2026 closure, mandatory five-day training, first-day per diem and
last-day bus reimbursement; attending training is not a guaranteed fieldwork hire.
No application functionality, employer assent, actual eligible applicant,
account-specific payout or legal terms were verified. Listing amounts are not
used as actual input or wages. Training destination and pre-departure cash
availability remain unknown. No fresh broad nightly research scan was performed.

## Alternatives, roadmap and next decision

The conditional [roadmap](../../coordination/POVERTY_ELIMINATION_ROADMAP.md)
stays at Stage 0: actual independent demand, worker consent, full costs and
spendable payout are the human bottleneck, not precision throughput. Existing
employer resources/advance/direct ticket and NO_LOAN/NO_GUARANTEE dominate an
invented gap. Funded escrow/payment protection may cover actual uncovered payment
risk but not pre-departure cash without access. Direct funding/sponsorship/cash
remain benchmarks under separate authority; credit/revolving guarantee remain
conditional on evidence, benefit, legal controls and M>1. All stages 0-7,
multiplier, learning and sustainability gates are unchanged.

Next bounded existing-helper decision: make the same-unit evidence assumption
explicit and fail closed on absent/mismatched unit attestations before interpreting
fare minus cash; never add guessed FX or a second finance engine. First finish
current exact review/main integration. Applicant/funding/recovery dependencies
retain their current owners, triggers, limits and deadlines; no recruitment or
contact to manufacture evidence. Stop further generic scans or infrastructure
when the actual evidence gate is absent; no positive net benefit is inferred.
