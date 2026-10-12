# Paid-first-job feasibility — Stage A execution packet

Status: ACTIVE, zero-spend / zero-contact preparation  
Date: 2026-10-11  
North-star role: test whether the agent network can help a new human freelancer convert useful work into spendable earnings and later independent buyer demand. Lending is not part of this pilot.

## Hypothesis

A small, real, sponsor-funded first job with rapid specification, quality review, payment, and a legitimate platform reference may reduce the cold-start barrier for a new online freelancer enough to generate independently funded follow-on demand.

This is a feasibility hypothesis, not a causal-effect claim.

## Current baseline

- independently funded qualifying jobs produced by this project: 0
- verified spendable human earnings caused by this project: $0
- qualified productive-credit cases: 0
- active lending decision: NO_LOAN
- existing smart-contract work remains optional infrastructure, not the active experiment

## Platform candidate: Upwork

Use Upwork only if the operator account can satisfy its current client requirements and the exact job complies with platform rules.

Current public rules checked 2026-10-11:

- A standard job post can be global; preferred countries/regions may be stated, but freelancers elsewhere may still apply.
- Job descriptions should be in English.
- Client phone/billing verification may be required before posting; identity verification can be required and, if not completed, may prevent posting, messaging, or working with freelancers.
- Freelancer identity verification can be required before proposals, accepting offers, or withdrawals.
- Payments must remain on Upwork unless the applicable off-platform conversion process is used.
- Withdrawal methods vary by country. Upwork lists local-bank transfer outside the U.S. at $0.99, plus PayPal, Payoneer, and M-Pesa in Kenya among possible methods.
- The freelancer service fee must be captured from the actual offer/contract shown to the selected worker; do not assume a fixed percentage.
- Do not scrape or republish platform profile data. Any research-like observation uses participant consent and data supplied by the participant or records the project itself legitimately receives.

Primary current references:
- https://support.upwork.com/hc/en-us/articles/211063408-How-to-post-a-job
- https://support.upwork.com/hc/en-us/articles/26040445438611-How-to-verify-your-identity-as-a-client-on-Upwork
- https://support.upwork.com/hc/en-us/articles/360001176427-How-to-verify-your-identity-as-a-freelancer
- https://support.upwork.com/hc/en-us/articles/211060918-How-to-get-paid-on-Upwork
- https://support.upwork.com/hc/en-us/articles/40445575013395-When-do-I-pay-a-Freelancer-Service-Fee
- https://www.upwork.com/legal

## Work class

Choose work the project would otherwise need and purchase, not make-work. Initial admissible classes:

1. human usability test of one public onboarding flow, with structured observations and reproducible steps;
2. source-check of a published blog claim set against supplied primary sources;
3. translation/localization of a public project page into a language the project has a credible reason to publish.

Before posting, select exactly one class and freeze:
- deliverable;
- deadline;
- acceptance rubric;
- maximum one revision round;
- sponsor reservation value;
- reviewer;
- expected review minutes.

## Proposed feasibility size

Six new entrants, each offered one genuine fixed-price task with a nominal worker gross of $60, conditional on operator approval of the exact cost card.

No waitlist, randomization, or causal-effect language in Stage B. No participant loses a promised review because of study assignment.

## Candidate first task — independent claim-source check

**Admissibility disposition: NOT ADMISSIBLE YET.** This is the first task to
evaluate, because an independent review could determine whether the project
keeps, corrects, or withdraws claims in a public explanation and its VERIFY
record. That is a concrete editorial use, but willingness to buy it, the maximum
reservation value, the gap left by ordinary internal or already-consented
reciprocal review, and the complete source/test bundle are not yet evidenced.
Do not describe the task as genuinely purchased work until those fields pass.

Freeze the candidate against these public revisions:

- vision commit `35ac4739012d71b853b7d98b494ea598d9e3472c`;
- post blob `3a7576453cb7761cda85e84c54c813d4f0d2f85d`;
- contract/design commit `68a968fbb3bb9aef7285dc2d2e1ceb3068e4789b`;
- design blob `ead483300eb2227855c6c736be0c8a4b266080b8`.

The ten audit targets are questions for the worker, not accepted facts:

| ID | Claim to assess | Starting locator |
| --- | --- | --- |
| C01 | Graph-only costless vouching cannot distinguish a fake ring from genuine community. | Design sections 2 and 7; cited original research. |
| C02 | Stake backs others, not the staker's own guarantee. | Design sections 4-5; capacity/backing code. |
| C03 | Paid contributions add capacity exactly 1:1. | Design sections 4-6; contribution and dues code. |
| C04 | A programme line is budgeted and cannot be attested onward. | Design sections 4-5; issuer-budget invariants. |
| C05 | Received backing is nontransitive, and paid-job counts add no capacity. | Design sections 4 and 6; negative controls. |
| C06 | The default loss order and any worker-dues exposure are adequately disclosed. | Design section 5, including pledged dues; claim accounting. |
| C07 | Worker acceptance, fixed backer shares, and bounded expiry address the reported attacks. | Design section 12 revision-2 regressions; remaining dispute gap. |
| C08 | Client groups constrain known aliases but miss a fresh identity in another group. | Design section 12 revision 4; alias negative control. |
| C09 | Sponsor share-loss and exit fixes prevent the stated cross-funder and dues subsidies. | Design section 12 revisions 3-5; capital/release invariants. |
| C10 | The 29-test/revision-2 and local-ring claims, later fixes, and future-deployment wording have exact revision/time scope. | Pinned VERIFY/test receipts and the actual revision-5 deployment receipt. |

**Worker-facing brief (freeze before posting):**

- Review the ten numbered factual claims supplied from the current public post
  `microcredit-vision/posts/2026-10-11-who-can-vouch-for-a-newcomer.md` at one
  pinned commit. Use only the supplied pinned contract, test, design-note and
  review sources; do not inspect private correspondence or personal data.
- Return one table row per claim with: `claim_id`, exact source URL and
  commit/section/test locator, `SUPPORTED | OVERSTATED | UNSUPPORTED |
  UNDETERMINED`, a two-sentence reason, and the smallest corrective wording
  when the result is not `SUPPORTED`. `UNDETERMINED` is appropriate when the
  supplied evidence cannot resolve the claim; document the exact bound.
- Run the supplied read-only local verification commands and report the exact
  command, exit status and output digest. Before posting, the buyer must pin a
  complete source bundle and preflight every command in the supplied
  environment. A worker reports `BLOCKED` with the exact error when that package
  fails; the buyer must not substitute commands after submission. Do not deploy,
  sign, spend funds, use credentials or contact anyone.
- Deliver Markdown plus the command transcript within 48 hours. One bounded
  revision round may correct missing fields or locator mistakes; it may not
  change the frozen claims or acceptance rules.

**Blinded acceptance rubric:** the reviewer receives the deliverable under a
random participant code and scores only the following predeclared fields:

1. all ten claim IDs appear exactly once;
2. every row gives a resolvable pinned source and precise locator;
3. every verdict follows from that source without strengthening its scope;
4. every non-supported verdict supplies a minimal usable correction;
5. the transcript contains every required command, exit status and digest;
6. there are no invented runs, sources, private data or unauthorized actions.

Accept when all six gates pass. An adverse or `UNDETERMINED` conclusion can
pass. Revise once for one specific curable field, evidence, locator, command, or
verdict error, including an honest correction from `SUPPORTED`; distinguish
mistake or good-faith disagreement from fabricated evidence. Reject for
fabricated evidence, a substantive integrity failure that remains after the
frozen revision opportunity, private-data exposure, or any unauthorized action.
An environmental `BLOCKED` result is scored separately and is not converted
into worker failure. The buyer names the dispute resolver and payment rule before
hiring. The reviewer records the failed gate and exact row; style and agreement
with the project's preferred conclusion are not acceptance criteria.

**Pre-price record:** worker gross candidate `$60`; deadline 48 hours; maximum
one revision; reviewer target 45 minutes. The buyer's maximum reservation value,
incremental value over internal/reciprocal review, fair value, live
client/platform fee, worker service fee, payout eligibility and timing, source
bundle/test feasibility, dispute resolver, payment rule and maximum support cost
remain `UNKNOWN`. Therefore this candidate is `NOT ADMISSIBLE YET`, is not
approval-ready and creates no authority to post, recruit, contact or spend.

## Acceptance rubric

The exact rubric must be frozen before recruitment and must be checkable without knowing participant identity beyond what Upwork legitimately displays to the client.

Common gates:
- deliverable submitted by deadline;
- required fields complete;
- factual statements trace to supplied evidence where applicable;
- no fabricated observations or sources;
- output usable by the project with at most one bounded revision round.

Record ACCEPT / REVISE / REJECT plus reasons. Pay according to the platform contract and any predeclared milestone terms; do not improvise payment rules after seeing the work.

## Participant economics record

For every participant record:

- contract gross;
- freelancer service fee shown for that contract;
- withdrawal fee/method if voluntarily supplied;
- time spent on paid work;
- unpaid proposal/onboarding time voluntarily reported;
- revision/support time;
- payout-available timestamp;
- payout-withdrawn/spendable timestamp if participant chooses to report it;
- spendable net = gross minus platform/service/withdrawal costs actually borne by participant.

Do not infer poverty status from country or profile.

## Project economics record

Record:

- worker gross payments;
- client/platform fees;
- reviewer minutes;
- support minutes;
- failed/rejected work cost;
- fair value of accepted deliverables, frozen before recruitment;
- total project cost;
- spendable worker dollars;
- incremental subsidy = total project cost minus fair value of accepted deliverables.

Report paid-work economics separately from unconditional-cash benchmarks.

## Consent and privacy

Before any research-like follow-up, obtain explicit consent for the six-week observation.

Minimum:
- participation in the paid job is not conditioned on agreeing to research follow-up;
- no public names, handles, precise location, identity documents, tax information, or private messages;
- follow-up may ask only for independent buyer inquiries/contracts/earnings and time/cost outcomes;
- participant may stop follow-up without affecting earned payment or reference;
- store only the minimum derived fields needed for the experiment.

Do not scrape Upwork or use platform API content for research/publication without any permission Upwork requires.

## Six-week exploratory outcomes

Primary feasibility outcome:
- at least 5 of 6 paid deliverables accepted under the frozen rubric and paid within the declared payout window.

External-demand signal:
- at least 1 participant reports and can verify an inquiry or paid contract from an independently controlled buyer during six weeks.

Other outcomes:
- spendable net worker earnings;
- time to spendable payout;
- support/rework burden;
- project cost / spendable worker dollar;
- participant-reported harm or material friction.

The external-demand signal is exploratory. Six participants cannot support a powered causal claim.

## Pass / stop rules

Proceed to design a larger preregistered test only if all of the following hold:
1. >=5/6 deliverables accepted under the frozen rubric;
2. all accepted workers receive promised platform payment;
3. worker and project costs are measured, not guessed;
4. no platform, consent, privacy, or identity rule failure occurs;
5. >=1 independently controlled buyer inquiry or paid contract is verified during follow-up.

Stop or redesign market-access infrastructure if:
- no legitimate platform/recruitment/payout path exists;
- selected work would be make-work;
- support/rework destroys attractive net earnings;
- any participant is materially harmed;
- independent demand remains zero through the full six-week observation window.

A stopped/null pilot does not reopen lending by default. Direct cash or ordinary direct sponsorship remains the benchmark.

## Exact pre-spend gate

Before any posting, contact, recruitment, contract, or spend, the operator must be shown one cost card containing:

- platform and account requirements;
- selected work class and frozen rubric;
- six-task gross budget;
- exact client/platform fees then visible;
- maximum review/support allowance;
- maximum total authorized spend;
- data/consent text;
- payout timing;
- stop conditions.

Only that exact card is approval-ready.

## Next executable action

Without contacting anyone or spending money, select one real project deliverable that would otherwise be purchased, write the exact fixed-price task and blinded acceptance rubric, and price the complete cost card using the live platform account screens available to the operator.

If Upwork's actual account, posting, identity, fee, payout, or research constraints make the packet non-compliant or uneconomic, replace Upwork rather than weakening the gates.
