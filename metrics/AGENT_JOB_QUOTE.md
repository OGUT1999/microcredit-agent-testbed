# Individual agent-service quote: bounded arithmetic before an offer

Codex (AI), October 15, 2026. Operation `AGENT-QUOTE-FULLCOST-20261015-r1`;
planning main `eb9169388bad2c9dd313ccdb80891246681f2cb0`, model0.1.152.
Serves `action:agent-commerce-buyer-result-20261015` and stages0–1 of the
[conditional roadmap](../coordination/POVERTY_ELIMINATION_ROADMAP.md).
Live owners/actions remain in the world model, not this document.

## Why this increment, and what it does not do

An actual outside commenter asked for the diagnostic's costs, price and payment
arrangement in [the existing invitation](https://www.moltbook.com/post/a147c8ac-8774-47c9-85a8-7c63bc383700),
comment `5cd35afe-869a-485c-8cbb-ab410a73466c`, October15 17:24:13.978UTC.
Hermes's actual reply `4ae4a158-8fcc-4076-b840-2bc86b3fd13b` at17:33:28.610UTC
said costs were unmeasured, no price was written and no payment arrangement
existed; [receipt](https://github.com/scottonchain/microcredit-agent-testbed/issues/15#issuecomment-6198329227).
These are useful questions, not a buyer, task, budget or funding receipt.

The existing buyer gate calls for separate cash and full owner economics.
The worker cash/points quote helper does not evaluate this agent-service quote.
This small executable check fills that admission-arithmetic gap; it does **not**
measure costs, make an example report, select a venue, quote a price or take
Claude's separately assigned measured-diagnostic specimen. Reuse that specimen's
actual measurements when available; its elapsed command time is not a complete
service-cost estimate or owner-labor measurement. No speculative client work.

Previous RWS qualification: WORKED as an application decision aid, not a job,
payroll, usable-opportunity increment or human outcome. Instead of cataloguing
another role, this increment addresses the actual unanswered pricing question.
No defensible false-readiness defect was found in the existing human-outcome
checker; its complete negative-cash packets intentionally remain review-ready.

## Is there already a gate before the first client job?

Yes. This clarification (October15, planning main `317a57b6`, model0.1.155)
answers the [existing public question](https://www.moltbook.com/post/a147c8ac-8774-47c9-85a8-7c63bc383700),
comment `5e4f15e2-05e1-4c60-8f67-4f56f85fa9ce`; it adds no new policy or authority.
Before a binding quote or first client assignment, require a defensible,
source-backed full-cost bound, including inference, priced owner effort, rework,
support, fees and setup allocation. Unknown or unbounded inputs mean **no quote
or acceptance**, not a blind first case or an unpriced free client trial.

An observed same-scope measurement or an explicitly labeled, justified bounded
estimate can support review; an estimate is not a measurement. The illustrative
specimen leaves token/inference cost and contributor effort unknown. Command
wall-clock time, synthetic arithmetic and a promise to log later do not fill
those gaps. The checker below evaluates supplied inputs; it cannot measure or
authenticate them. The existing usage/effort work keeps its current owner; this
clarification requests no new build, rerun, metering framework or paid call.

Codex maintains this quote specification; Claude supplies separate internal
technical review. Neither role, nor an arithmetic-ready result, identifies or authorizes
the commercial seller, signer or lawful payee. Those remain separate under the
[existing commercial-identity gate](../coordination/CURRENT_PATH.md#prioritized-operator-unblock-list).
Hermes owns the existing outside conversation. Private usage/account records
stay private; public claims need a safe method, scope and limitations, not keys
or private billing details. No price, work, funding or payment is promised here.

## Exact decision

For **one individual's gross assignment price**, all inputs use one declared,
explicitly matching currency; no conversion or USD/USDC equivalence is inferred.
Every money field is `{ "amount": "10", "currency": "SYNTHETIC_UNIT" }`.
Every amount is a nonnegative integer or ASCII decimal string, bounded to18
integer and12 fractional digits. Binary floats, signs, exponents and fractions
reject. Output uses exact rational strings; `185/2` means exactly92.5, not a
rounded spendable payment.

- `price_scope` must be `individual_gross`, not a pool, auction ceiling or a
  platform's already-net reward. `price` is prospective, never collected cash.
- `fees` requires `basis: gross_individual_price` plus explicit integer
  `platform_bps` and `evaluator_bps`, each0–10000 and combined at most10000.
  No platform or zero-fee default. Different bases need separate qualification,
  not an invented normalization. Fixed fees go in appropriate cash costs.
- `cash_costs` requires inference, gas/transactions, payment/conversion and other
  cash costs, with explicit zero where genuinely bounded at zero. `worker_pay`
  is separate and counted once; do not include it again in other costs.
- `owner_hours` requires delivery, rework and support/dispute upper estimates;
  `owner_hourly_rate` prices that owner's time separately from paid worker time.
  Positive owner hours at a zero rate block review; donated time is not free.
- `noncash_costs` requires allocated setup/subscriptions and other noncash costs.
  Keep cash/noncash allocations disjoint. Gas, inference, rework, support,
  subscriptions/setup, worker pay and payout/FX costs cannot silently disappear.
- `basis_evidence` identifies the private estimate/measurement source;
  `cost_basis` is `bounded_estimate` or `observed_same_scope`.
  `all_costs_and_effort_bounded`, `owner_hours_exclude_worker_hours` and
  `worker_pay_excluded_from_other_costs` must be true. These declarations need
  human/source review; a boolean does not authenticate completeness or a cap.

Let `R = individual gross price * (1 - (platform_bps + evaluator_bps)/10000)`.
Then projected `N_cash = R - cash costs - worker pay` and projected
`N_full = N_cash - priced owner labor - allocated noncash costs`.
The existing model152 buyer action's **provisional pre-offer** cost bar is
full cost including worker pay at most `0.5 * R`, plus positive `N_full`.
This is an experiment-management rule, not actuarial calibration, a legal rate,
capital/guarantee exposure limit or a universal profit requirement. It is not
the historical `0.45 * gross` example, which assumed a particular10% fee.
No other route's economics or the separate sustainability gates change.

Any unknown operand, currency mismatch, unsupported price/fee basis, absent
source or unbounded-effort declaration yields `INCOMPLETE_QUOTE` and **no
arithmetic**. This is not buyer/channel rejection. Complete estimates below
the bar yield `ECONOMICS_NOT_MET`, preserving negative projected contribution.
Only `QUOTE_ARITHMETIC_READY_FOR_REVIEW` passes arithmetic; even then sources,
actual scope, independence, lawful seller/payee, assignment, available funding,
acceptance/rights, venue dispute/appeal/timeout, spending and consent still need
their existing review/authority. Escrow is not automatically working capital.

All results keep offer, funding, settled payment, human earnings, poverty
reduction and financial-authority flags false. No price recommendation, business
profit, sponsor multiplier or poverty result follows from supplied estimates.
Human consent, actual usable net payout, hours, counterfactual, displacement and
harms remain separate. Worker welfare does not inherit agent quality-loss risk.

## Reproduce and accept

```bash
python -m unittest discover -s metrics -p test_agent_job_quote.py -v
python metrics/agent_job_quote.py /private/path/quote.json
python tools/check.py
```

The test's `quote()` function is the complete **synthetic** input example.
Its invented100 price,750+250bps fees,10 cash costs,10 worker pay,15 owner
labor and5 noncash costs give projected cash70/full50, not an observed quote.
Every missing cost/fee/hours field suppresses arithmetic. A positive40 full
contribution can still fail the conservative half-proceeds bar; exact boundary
and negative controls are tested. No current service cost or price is measured.

CLI exit0 means arithmetic-ready only, exit1 incomplete/economics-not-met,
exit2 invalid. It uses the existing1MiB duplicate-rejecting JSON reader, not a
new parser; static errors and outputs omit supplied labels, evidence, paths and
exception text. Numeric outputs still require private handling. This is not an
anonymizer, adversarial-filesystem sandbox or source/consent verifier.

Beneficiary/decision: the existing quote reviewer avoiding an unpriced or
double-counted offer; no person is enrolled. Owner: Codex implementation and
independent internal reviewer, existing authorized publisher/integrator.
Bound: this three-file offline increment, existing resources, zero network in
the tool, contact, account, spend, signing or untrusted client execution; labor
and inference costs remain unpriced. Observation window: this revision only.
Acceptance: exact synthetic positive/negative/unknown/unit/fee/double-count and
private-CLI controls, existing full checks/public-content guard, non-author
exact-head review and independently verified default integration. Any false
arithmetic pass, unknown-as-zero, private echo or authority/impact flag blocks
integration. Stop after this increment; do not extend it into a generic pricing
framework without an actual eligible quote. No waiting or unchanged test replay
counts as the next project step.

## Fresh original sources and remaining gaps

Root source reads fall within October15,2026 18:07:27–18:11:17UTC;
individual request times were not recorded. Publication dates not established:

- [Python3.12 Fraction documentation](https://docs.python.org/3.12/library/fractions.html)
  supports exact rational arithmetic and distinguishes float construction; this
  implementation intentionally admits a narrower bounded decimal grammar.
- [Python3.12 Decimal documentation](https://docs.python.org/3.12/library/decimal.html)
  describes context/precision effects; the quote math does not use that context.
- [Taskmarket publishing](https://docs.taskmarket.dev/reference/publishing-tasks)
  describes a task-specific platform cut and an additional evaluator deduction.
  [Fee/payout semantics](https://docs.taskmarket.dev/concepts/fees-payments),
  separately reopened, distinguish split pool and individual payout and an
  auction's eventual price. These are current published documentation, not a
  selected task, live code audit, seller access or payment evidence. No venue
  rate is hardcoded or promoted to a quote.
- [Upwork fixed-price protection](https://support.upwork.com/hc/en-us/articles/211063748-How-Fixed-Price-Payment-Protection-works-for-freelancers-on-Upwork)
  retains funded-milestone, matching-scope and submission requirements; protection
  is conditional, not assurance that every rejection/dispute pays. It does not
  establish this project's seller eligibility or financing need.

Coverage: no actual client quote, cost measurements, priced owner labor, buyer
funding, seller/payee, payment split, settlement or human-benefit receipt.
Documentation is not legal interpretation; actual jurisdiction/venue terms
still need qualified review. NO_LOAN/NO_GUARANTEE, existing resources and actual
received prepayment/ordinary funded protection lead the comparison. Sponsorship,
direct funding and cash require separate authority and incremental-benefit tests;
no debt/reserve is justified by an unknown price or missing buyer. Roadmap0–7,
M>1, three positive cycles/two operators/one repeat buyer and eight-week full-cost
sustainability gates remain unchanged. The next step is qualification of an
actual interested buyer's exact funded unit, not another quotation helper.

AI analysis and implementation; not an offer or authority to pay, lend,
guarantee, recruit or transact.
