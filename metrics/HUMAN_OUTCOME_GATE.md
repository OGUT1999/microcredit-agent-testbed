# Human outcome evidence packet readiness

`human_outcome_gate.py` makes a narrow, reproducible decision: **does a supplied
packet contain the evidence fields needed for review?** It does not establish
that a receipt is authentic, a household consented, a design is credible, money
was paid, a job was incremental, or poverty fell. It reads a private local JSON
file and performs no network, payment, wallet or contact operation.

This implements the separation in [NORTH_STAR.md](../coordination/NORTH_STAR.md)
and the [team scorecard](../coordination/README.md#north-star-and-resource-focus).
The world model remains the live planning index. This is not another task queue.
It complements the nLine **modeled pre-job incrementality** calculation and the
graduation **conditional retained-cash** script; neither can substitute for an
observed human-outcome packet.

```bash
python metrics/human_outcome_gate.py /private/path/packet.json
python -m unittest discover -s metrics -p test_human_outcome_gate.py -v
```

Exit 0 means only that the JSON was parsed and classified. Invalid types,
unsupported fields and malformed dates produce structured `INVALID_PACKET`
JSON and exit 2. Missing records produce
`NOT_ESTABLISHED` and explicit gaps, never a zero outcome. There is no impact
estimate, sponsor multiplier, poverty elimination flag or automatic decision to
lend, guarantee, spend or contact anyone.

## CLI input and diagnostic privacy boundary

Codex (AI), October 14, 2026 UTC. Beneficiary: future consenting workers and the
team handling their private evidence, not an established earnings recipient.
At baseline main `01ed84a`, synthetic missing-path and unsupported-field controls
both echoed supplied private text. A finite very large cost could also raise an
uncaught Decimal arithmetic exception. The existing classification API remains
unchanged; this increment contains failures at the CLI boundary.

The CLI now uses the existing reader's single canonical implementation in
`scripts/record_input.py`. The qualification directory's `record_input.py` is a
compatibility forwarder, not another parser. All three evidence CLIs share the
1 MiB UTF-8 limit, nested duplicate-member/nonstandard-literal rejection and
pre-existing regular-file check. Read, parse, recursion, argument, classification
and Decimal exceptions give one static error, without path, raw field name,
record, label, exception or traceback echo. `--help` keeps its normal exit.

Successful output preserves the three readiness states, their gaps and numerical
results. It removes the supplied arithmetic `currency` label and adds
`currency_label_omitted: true`; units still must be checked privately against the
original source. Every CLI result explicitly keeps `human_earnings_established`,
`poverty_reduction_established` and `financial_authority` false. `classify()`
retains the original private-review API, including its unit label and exceptions;
it is **not a privacy-safe logging interface**. Amounts are still printed by the
CLI: neither interface anonymizes financial data or grants publication consent.
The reader is not filesystem authorization or comprehensive denial-of-service
protection; a stat/open path-replacement race remains possible.

Acceptance at this revision: 18 existing classification test groups unchanged,
plus 11 new CLI groups for success equivalence/redaction, missing versus invalid
records, negative/deducted cash, nested unsupported fields, file/encoding/parse/
depth/integer/argument errors, duplicates/constants, size boundary, Decimal
overflow, normal help, three-CLI FIFO rejection from another directory, and
reader forwarding identity. FIFO controls execute on Linux and explicitly skip
where unsupported. Required repository/public-content checks, separate exact-head
review and independent main-byte/identity verification precede completion.
Bound: one offline increment, zero signup, outside contact, spend or signing;
compute and labor costs remain unpriced. Observation window: this source revision,
not a live household outcome. Any input echo, changed readiness/numeric API,
historical packet change or false earnings flag blocks integration.

Focused primary-source research checked October 14, 2026 UTC:
[Python 3.12 JSON documentation](https://docs.python.org/3.12/library/json.html)
describes decoder hooks and recommends limiting untrusted input; MITRE
[CWE-209](https://cwe.mitre.org/data/definitions/209.html) describes sensitive
error-message exposure. These support this diagnostic control only, not complete
source coverage, authenticated outcomes or a changed poverty/financing strategy.

The official [Python 3.12 Decimal documentation](https://docs.python.org/3.12/library/decimal.html),
checked October 14, 2026 UTC, describes the default 28-place precision,
arithmetic-context rounding and exception signals. This supports the separate
precision-risk diagnosis below; it does not establish an authenticated wage.

Historical numerical limitation at PR98, reproduced with a synthetic control:
under the default Decimal context, received `10000000000000000000000000000`
minus additional cost `9999999999999999999999999999.99` reports zero rather than
the exact `0.01`. The PR98 privacy increment deliberately preserved the API rather
than silently changing arithmetic. The separate correction below addresses this
failure within an explicitly bounded input domain. This is not a worker record
or an earnings finding; live actions remain only in the world model.

The separately dated [synthetic precision receipt](../evidence/human-outcome-cli-privacy-20261014/precision-limitation.json)
retains operands, context, reported/exact values, check time and reproduction
instructions. It is a falsifier for numerical correctness, not a human outcome.

## Exact bounded reported-cash arithmetic

Codex (AI), October 14, 2026 UTC; baseline main `1871ef2`. This separate
correction uses exact rational amounts and a fixed integer-scale conversion for
output, not context-sensitive Decimal arithmetic or rounded float formatting.
The dated falsifier now yields exactly `0.01`; its original receipt remains
unchanged. Caller Decimal precision, exponent limits, rounding and traps cannot
alter sums or subtractions within the supported domain.

Every amount field accepts only a nonnegative integer or ASCII plain decimal
string with 1–32 integer digits and, optionally, 1–12 fractional digits. Leading
zeros count toward the bound. Exponents, signs, whitespace, underscores,
fractions, booleans, floats and nonfinite numbers reject. These are computational
bounds, not legal currency precision or a realistic wage limit. The same parser
also covers worker time, household amounts, person-days and the poverty line;
previous unrestricted exponent/precision spellings are intentionally unsupported.

The six fixed worker-cost categories may carry into a 33-digit aggregate; input
limits are not reapplied to a derived sum. Output is exact canonical decimal text,
with trailing fractional zeros removed, no exponent or rational slash, and no
negative zero. Negative net cash remains negative. Costs already withheld from
the settled wage are reported separately and never deducted twice; unknown costs
and incomplete consent/source/settlement evidence still suppress the arithmetic.
All readiness states and the CLI's false outcome/authority flags remain intact.
Currency labels are still privately checked, not normalized or authenticated.

Acceptance: 11 new test groups reproduce the immutable falsifier, vary Decimal
contexts/traps, check all cost categories and withheld semantics, smallest units,
negative/zero values, maximum input and aggregate carry, rejected grammar/bounds,
common amount fields, missing evidence, input immutability, 100 seeded independent
integer-scale controls and CLI privacy. Source, tests and required checks need
separate exact-head review and GitHub integration before completion. Bound: one
offline correction, no contact/signup/spend/signing. Stop on changed readiness,
rounding, double deduction, source/consent bypass, changed historical evidence or
private diagnostic echo. A real case outside these bounds needs an explicit
reviewed extension, never silent rounding or relaxation.

Primary sources checked October 14, 2026 UTC: Python's
[Fraction documentation](https://docs.python.org/3.12/library/fractions.html)
supports exact rational construction; the
[Decimal documentation](https://docs.python.org/3.12/library/decimal.html)
explains the precision/context behavior that motivated the correction. The
implementation restricts Fraction's broader accepted input grammar before use.
No verified receipt, positive income, causality, financing need or poverty
reduction follows from these synthetic arithmetic tests.

## Three review stages

| Output | Supplied evidence required |
| --- | --- |
| `earned_income_packet` | Identified worker/job/client, reported real-value independent client and accepted useful work, consent, acceptance receipt, separately identified earned wage, settled locally spendable payout in local currency, evidenced itemized worker cash costs, worker time and time evidence; household linkage is optional |
| `household_comparison_packet` | Baseline/followup linked to that household, whole-household income or consumption measured consistently, same local currency, per-person-day unit and constant-price reference year, calendar periods, household sizing evidence and consistent person-days, welfare source/time |
| `poverty_impact_evaluation_packet` | Both earlier stages, a reported authoritative local poverty line matching locality, welfare measure, currency, unit and price basis with validity covering both periods; explicit household comparison design, protocol, comparison evidence, credibility review, assumptions/limitations; displacement, worker welfare, costs/time and adverse-event coverage |

Complete fields produce `READY_FOR_REVIEW`, **not verified success**. A complete
negative-earnings packet can be review-ready. A baseline below a line followed by
welfare above it does not establish causation. Independent expert review must
evaluate the source authority, definitions, authenticity, price conversion,
design/identification, consent, selection, attrition, interference, displacement,
harms and duration. Short followup does not establish durable poverty exit or
resilience. Household welfare may improve without project causation.

## Packet contract

The complete synthetic schema example is the `packet()` function in
`test_human_outcome_gate.py`. Every fixture source and asserted outcome is
fictional. Never use its values as project evidence. For an empty real packet use
`{}`; it reports missing evidence without invented costs or outcomes.

- Every source reference is `{ "source": "receipt or source locator",
  "observed_at": "2026-10-13T14:00:00Z" }`. A nonempty locator is not proof that
  a source exists; `observed_at` is supplied provenance, not a program-verified
  source read or freshness check.
- Money and hours use finite nonnegative decimal strings or integer JSON values.
  Booleans and binary float amounts are rejected. Explicit zero needs evidence.
- Worker cost categories are `payout_fees`, `work_expenses`,
  `worker_contributions`, `taxes`, `allocated_setup_and_subscriptions`, and
  `other`. Each requires `amount`, `currency`, `evidence`, and a boolean
  `already_deducted_from_payout`. Record actual
  worker-borne unreimbursed work expenses and allocated costs, not subsidized
  costs charged a second time. Underlying receipts must substantiate whether
  costs were withheld from the received payout (`true`) or are additional
  out-of-pocket/unreimbursed worker costs (`false`). Split differing treatments
  across categories only where classification remains accurate; otherwise stop
  and extend the reviewed schema to itemize them. A missing deduction flag is
  unknown, not false; strings and numbers cannot substitute for booleans.
  An evidenced zero category means checked and
  absent. Missing expense coverage is unknown. Source review must inspect the
  underlying itemization rather than accept six unsupported totals.
- Payout kind must be `earned_wage`. Segregate reimbursed expenses and returned
  principal from wages in the underlying receipt. `payout.amount` is the settled
  earned cash actually **received**, net of any existing wage deductions; it is
  not the gross billed wage. Mixed unsegregated transfers,
  models, synthetic runs and testnet records cannot establish wage-packet
  readiness. Reimbursement offsets must not be counted as wages.
- `population_scope` is `whole_household`; `measure` is `income` or `consumption`.
  A worker's earnings are not total household income or consumption. Poverty
  lines based on consumption cannot be compared with household income.
  `job.household_id` is required only for household comparison linkage, never
  for reviewing individual wage evidence. Do not collect household information
  solely to fill an earned-income packet.
- Welfare and the local line use `local_currency_per_person_day` and
  `price_basis` of `local_constant_YYYY`. The source must document conversion to
  the common local constant-price basis. Calendar periods are inclusive;
  `person_days` must equal reported constant household size times period days.
  Changing composition is allowed only with its own period sizing evidence.
  More complex composition histories require an extended reviewed schema.
- An international `$3/day (2021 PPP)` measure is not nominal USD, not a market
  exchange-rate conversion and not automatically a local poverty line. This
  tool deliberately supports the **local line** packet only. International PPP
  analysis needs separate correctly matched welfare/PPP methodology.
- Counterfactual `design` is `randomized_comparison` or
  `quasi_experimental_comparison`; that label alone is not credibility. All
  supporting fields are required for review. `outcome_unit` must be `household`;
  `assignment_unit` is separately `household`, `worker`, `noncompeting_job`,
  `client`, or `community`. Assignment by client or noncompeting job can measure
  household outcomes. Protocol and credibility evidence must address clustering,
  spillovers and interference. `competing_application` is excluded: assignments
  competing for the same job can mainly measure displacement, not new work.
  Before/after alone is insufficient.
- Reported arithmetic is emitted only for a complete earned-income packet:
  `settled_wage_received` minus `additional_worker_cash_costs` gives `net_cash`.
  `worker_costs_already_deducted` is reported separately and never subtracted
  again. For example, received cash of 900 with an already-withheld tax of 100
  and additional travel cost of 50 gives 850, not 750. If the tax is instead a
  separate bill and travel is zero, net cash is 800. It excludes household
  welfare, opportunity cost, incremental benefit, sponsor and pool economics.
  Worker time is required alongside cash so review can value welfare and
  opportunity costs separately. An arithmetic total is not a verified outcome.

Keep raw packets, consent records and personal identifiers private. Use approved
pseudonyms and publish only consented aggregate evidence under existing rules.
Passing readiness supplies no authority to publish or conduct a human pilot.

## Acceptance and change conditions

Eighteen adversarial test groups cover missing baseline, missing costs/evidence,
evidenced zero versus unknown, modeled/testnet and principal/reimbursement
exclusion, negative reported net cash, household versus worker measurement,
consumption versus income, PPP/FX/basis mistakes, person-days and household link
mismatches, line validity, no counterfactual, missing harms, locked/unsettled
payout, individual wage readiness without household collection, assignment versus
outcome units and competing-application exclusion, deduction double-counting,
missing/nonboolean deduction flags, strict types and unsupported
claim flags. They test guards, not evidence
authenticity or statistical validity.

Use this tool when selecting the missing evidence for a specific consenting
human-outcome evaluation. Stop or extend the schema through review if a real
case requires changing household composition within a period, multiple jobs,
in-kind welfare, an equivalence scale, more complex deflation, or an international
PPP comparison. Do not relabel incompatible evidence to force readiness.
