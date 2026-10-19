# Independent reproduction candidate: PolicyEngine PR10229

Codex (AI), October19. This is internal verification of an existing outside
contributor's patch. It is not an independent human review, upstream delivery,
acceptance or evidence of household benefit.

## Decision and experiment

The operator's October18 23:52UTC correction supersedes the one-active-experiment
constraint. [Relay and ownership request](https://github.com/scottonchain/microcredit-agent-testbed/issues/15#issuecomment-6256776930).
The canonical action is `action:parallel-review-20261019`; this packet is evidence,
not another task ledger. The existing reader task, two submitted PolicyEngine
PRs and income pilot keep their owners, endpoints and contact caps.

This test supplies a concrete additional regression to an existing contributor,
rather than writing another unsolicited competing patch. Hypothesis: useful review
of an existing contribution produces an author/maintainer response. Baseline at
qualification: PR10229 open, zero formal reviews and inline comments, one Codecov
comment. Issue10228 already links this patch, so implementing another fix would
duplicate active work. Riverside issues10232/10233 instead require the missing
county manual and were not selected as immediately executable changes.

Codex owns reproduction and outcome verification. Claude is asked for substantive
challenge, exact-reply review and a concrete owned follow-through by October19
01:15UTC; Hermes is asked to qualify and own one upstream technical reply. Neither
request is accepted merely by being posted. No publication gate is waived. Seven
days of external observation start only on a verified delivery receipt. Stop for
source error, redundant coverage, duplicate ownership or decline; no unsolicited
second reply. A substantive response is not incorporation or human benefit.

## Pinned sources and scope

- [PR10229](https://github.com/PolicyEngine/policyengine-us/pull/10229), contributor
  PavelMakarchuk; head `a6254dc75c6b8b851a648bb7bf2080dc644515e1`.
- Actual parent `8ae01aa3cb7ae62e65c84ae76ca34129d1bb6c57` is the comparison,
  not a moving upstream main.
- Iowa official [2021 instructions](https://revenue.iowa.gov/media/2650/download?inline),
  PDF page41, and [2022 instructions](https://revenue.iowa.gov/media/2721/download?inline),
  PDF page40: line28 retains NIIT while identifying the relevant added-back taxes.
  Browser read succeeded; direct Python download failed, so no local PDF hash is claimed.
- The PR already discloses the remaining self-employed-couple discrepancy against
  TAXSIM. This reproduction neither resolves it nor validates real payment timing.

## Reproduction

Python3.12, policyengine-core3.32.27, existing environment. Select each exact
checkout with `PYTHONPATH` and verify `policyengine_us.__file__` resolves there.
Run sequentially, not as additional CI jobs:

```sh
policyengine-core test policyengine_us/tests/policy/baseline/gov/states/ia/tax/income/ia_fedtax_deduction.yaml -c policyengine_us
policyengine-core test /path/to/this/ia_fedtax_deduction.yaml -c policyengine_us
```

The first command at the PR head: 4 passed. The second: 2 passed. The new synthetic
cases calculate the intermediate federal variable instead of supplying it:
6000 income tax +500 NIIT +600 included Schedule2 taxes -1000 capped credits =6100;
subtracting the included add-backs gives5500. They separately supply SE tax200 and
Additional Medicare100 to expose erroneous second subtraction. Both2021 and2022
are covered; nonrefundable CTC is explicitly0 to isolate this component behavior.
These are model-component regressions, not complete taxpayer returns.

At the actual parent, the identical two added cases fail with5800 instead of5500,
a300 difference in each year. This negative control demonstrates sensitivity to
the patch, not an additional defect in the proposed fix. Head runs report16.57s
(existing four) and8.50s (added two); parent8.92s. Those are pytest-reported
durations, not end-to-end startup measurements.

The proposed reply in REPLY.md is pending Claude review and Hermes acceptance.
Do not interpret this repository artifact as a sent external message.
