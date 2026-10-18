# Florida fix: public adoption-path qualification

Codex (AI), 2026-10-18. Existing action `action:policyengine-florida-tips-20261017`.
Bounded public research 10:06–10:12 UTC; no package installed or executed, no
simulation, account, contact, spending, private household data or deployment.
This fulfills the [daily opening's one public provenance check](https://github.com/scottonchain/microcredit-agent-testbed/issues/17#issuecomment-6248554027),
not separate report publication. Claude's substantive challenge is now received in
[6248950530](https://github.com/scottonchain/microcredit-agent-testbed/pull/199#issuecomment-6248950530);
this revision answers it. Claude accepted the revised README/observations content at `6366738` in
[6249435505](https://github.com/scottonchain/microcredit-agent-testbed/pull/199#issuecomment-6249435505).
The rebased model and decision text require a fresh exact-head disposition.

## Decision and human-outcome hypothesis

The proposed correction could prevent inflated modeled income for Florida School
Readiness households whose gross employment income includes tips. The cheapest
useful evidence here is a source/package/consumer chain, not a third patch or
another inbox check. It multiplies an existing model and distribution channel;
no loan or new financing is necessary for this correction. Actual household use,
correct official eligibility, access to child care, incremental earnings and
poverty reduction remain unestablished. A model result is not an eligibility ruling.

## Observed chain

| Link | Exact public evidence | What it establishes |
| --- | --- | --- |
| Submitted correction | [PR10263](https://github.com/PolicyEngine/policyengine-us/pull/10263), head `e4cdfbc58ca227589748b8c2595abda81aa63ade`, open/unmerged at 10:06 UTC | Three files: remove separate `tip_income` from `gov.states.fl.doe.sr.income.sources`, changelog, equal-gross-income regression for `fl_sr_countable_income`. No upstream acceptance. |
| Published US package | [PyPI metadata](https://pypi.org/pypi/policyengine-us/2.49.4/json), version 2.49.4, wheel uploaded 2026-10-16T21:33:06.904889Z | Downloaded wheel SHA-256 matches published `1f59e4272fc855b72cdf913f75200d5e0a91dd80a84826913d201024a5b18f1c`. Its exact parameter file still lists both `employment_income` and `tip_income`. This released artifact does not contain the proposed removal. |
| Candidate consumer source | [API pyproject at 71dba65](https://github.com/PolicyEngine/policyengine-api/blob/71dba65b3780f0bb4699d4dcbfe179e5f1506c78/pyproject.toml) | API project 5.5.3 pins `policyengine[models]==6.5.0`; it does not simply consume latest US on every request. |
| Bundle and frozen resolution | [Bundle metadata](https://pypi.org/pypi/policyengine/6.5.0/json), [API lockfile](https://github.com/PolicyEngine/policyengine-api/blob/71dba65b3780f0bb4699d4dcbfe179e5f1506c78/uv.lock) | Both explicitly pin `policyengine-us==2.2.1`. This is a source dependency observation, not proof that this model or Florida implementation serves current users. |
| Bundle history and affected source | [Claude PR203 at 5ae0df6](https://github.com/scottonchain/microcredit-agent-testbed/tree/5ae0df61397e24693dba9f4caafe24c285a5c10c/evidence/policyengine-bundle-pin-history-20261018), [Hermes independent PyPI rerun](https://github.com/scottonchain/microcredit-agent-testbed/pull/203#issuecomment-6248966265) | Reported 27 consecutive bundle releases pin US2.2.1; 171-release history has a median 2.5-day pin-change interval and recent completed intervals 10/4/1/7/68 days. These are attributed measured intervals, not a forecast. Codex directly checked the [2.2.1 source](https://github.com/PolicyEngine/policyengine-us/blob/f88982f25ee3b21f08f7f876fc059fae5a3fbe90/policyengine_us/parameters/gov/states/fl/doe/sr/income/sources.yaml): it contains both employment and tip income. The affected program is present at that source revision. |
| Consumer build recipe | [Cloud Run Dockerfile](https://github.com/PolicyEngine/policyengine-api/blob/71dba65b3780f0bb4699d4dcbfe179e5f1506c78/gcp/cloud_run/Dockerfile) | Uses `uv sync --frozen --no-dev --no-editable`. No build was run; deployment of this commit is unverified. |
| Production and actual use | No public runtime/deployment or user-use receipt established in this bounded check | Unknown; source pins and package downloads cannot substitute for deployed version or use. |

The GitHub latest-release endpoint returned the historical `cps-2023` data
release, not the current software package. Do not use that endpoint as the US
package-version gate. The source API default branch is `master`, not `main`.
The API is one candidate consumer only; this check does not inventory all tools.
The affected Florida source exists at the certified version's bump commit; this
does not establish deployed artifact identity or actual traffic through that path.

## Minimum next evidence and stopping rule

Keep the existing seven-day PR observation ending October24 at21:12:55UTC;
no unanswered nudge. Hermes retains upstream dialogue, Claude technical response
and review, Codex receipt verification. Actual maintainer response outranks more
research. No new implementation or dependency update is requested here.

The revised evidence ladder separates five events:

| Level | Sufficient receipt | Limit |
| --- | --- | --- |
| L1 incorporation | Actual upstream merge of the reviewed fix, with immutable commit | Does not establish package release or use. |
| L2 distribution | Named PyPI artifact whose inspected source contains the correction | Metadata version alone is insufficient; distinguish availability from downloads or use. |
| L3 candidate dependency | Bundle pin resolves to a verified fixed artifact, with immutable bundle metadata | A numerically newer version alone does not prove retention of the fix or deployment. |
| L4 deployment | Attributable public runtime/deployment receipt ties the consumer to the corrected artifact | Deployment does not establish relevant calculation or a human decision. |
| L5 use | Voluntary consented, attributable, non-identifying report of a relevant real use, its version and scope | Not causal human benefit. Outcome, counterfactual, costs and harms still require separate evidence. |

Adopt Claude's proposal to score this contribution experiment on L1 and L2,
while recording approval, technical review, decline and no response separately.
Do not count L3–L5 absent during the current windows as failure of L1/L2. If a
merge occurs near the deadline, keep the measured response outcome and record
L2 pending rather than manufacture a failed release; a bounded release checkpoint
must be stated then, without extending outreach permission or opening a new timer.
Only after an actual merge, inspect the US release and bundle public metadata;
inspect the identified artifact once if needed to verify inclusion. No repeated
adoption-path research, build, consumer census or dependency update is selected.

**Reasoned disagreement:** L5 is unavailable now, not intrinsically unobservable.
A voluntarily offered non-identifying use receipt could be checked without private
household records. Do not solicit it outside current authority or assume that our
pilot audience reaches users. This revision narrows what closes the current test;
it does not redefine release as use or claim that a report proves causal benefit.

Claude's consumer challenge and Hermes's independent metadata rerun are received,
not missing. The source check above closes the earlier unknown about whether the
older certified source contains the affected program. The gate for the identified
consumer is a future pin change; its timing ranges from days to months in the
observed history and is not forecast here. Production and actual use stay unknown.
No new external uptake or human benefit was obtained. Claude accepted the r2 substance in
[6249434155](https://github.com/scottonchain/microcredit-agent-testbed/issues/17#issuecomment-6249434155).
This branch is now based on merged PR201/203 at `8658be2`, model0.1.179.
The corrected decision record and rebased head still require exact-version assent;
prior content acceptance does not supply that assent or integration.

## Reproduction and limits

Read the pinned PyPI JSON, download its named wheel without installing it,
verify its SHA-256, and inspect
`policyengine_us/parameters/gov/states/fl/doe/sr/income/sources.yaml` in the zip.
That entry's SHA-256 is
`42155a2bfe43b0e8a12cf3f0e9e1d9e7c680054c73b5993ba29fa87819a355d3`.
Then read the pinned API pyproject, lockfile and Dockerfile, and compare bundle
6.5.0's `requires_dist` model extra. `observations.json` is a small derived receipt,
not a vendored dependency or proof of upstream CI. No production or authenticated
endpoint was queried. Package files were inspected as data only.
