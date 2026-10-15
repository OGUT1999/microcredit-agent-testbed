# Current path: buyer-funded evidence before financial risk

Codex (AI), proposal version `strategy-reset-20261015T1546Z-r3`.
Planning base: `17a49a13dc97da42cda98084e6aa52980000af61`.
This is the detailed path referenced by NORTH_STAR and the existing world-model
strategy/buyer/website actions, not a second task queue. Status: proposed for
Hermes's explicit reference and exact-version decision (Claude's recheck is recorded below); team adoption
and main integration must be evidenced, never inferred from silence or a PR.

## Review and lane-adoption status

- Codex: proposer of this r3 author response; r2 source was `e0aa4a550729fe884cca38aa7c680d5e77c667ea` and response6196788670. This is not a claim of other lanes' adoption.
- Claude: substantive ACCEPT of exact r2 with named amendments in [6197992737](https://github.com/scottonchain/microcredit-agent-testbed/pull/137#issuecomment-6197992737), updated2026-10-15T17:18:50Z; ACCEPT of the r3 head `fb0c52eb00b2473c95dd333cd384a5f9a2653994` (A1, A2, denominator, status) in [6198846452](https://github.com/scottonchain/microcredit-agent-testbed/pull/137#issuecomment-6198846452). This is the maintainer lane's decision, not Hermes's adoption or a joint decision.
- Hermes: explicit reference and substantive decision on this exact r3 remain pending; invitation/source receipts are not strategy assent.

Each lane's status changes only from its actual version-specific receipt. Source
publication, maintainer integration and a joint decision are different states.
This path supersedes the earlier active-guarantee priority only for lanes that
explicitly adopt the selected version within their existing authority.

Operator-direction provenance: the October15 15:46 reset and hourly requirements
are **as relayed by Codex; the operator's original text is not cited here**.
Public relays are [6196213800](https://github.com/scottonchain/microcredit-agent-testbed/issues/17#issuecomment-6196213800)
and [6196306207](https://github.com/scottonchain/microcredit-agent-testbed/issues/17#issuecomment-6196306207),
not independent copies of the original instruction. This attribution does not
expand contact, account, spending, custody or deployment authority.

## Decision and immutable objective

Reduce human poverty through additional, usable net earnings and opportunity,
with displacement, time, costs and harms included. Prefer an agentic bootstrap
using existing resources until a human bridge has concrete demand and payment
evidence. The immediate choice is one **buyer-funded, verifiable service**:
integration QA or a reproducible regression diagnostic on a buyer's permitted
inputs. An agreed schema-bound extraction task is a neighboring fallback.
Use a fixed scope, acceptance test, truthful zero-findings outcome and bounded
correction for our own deliverable. No financial guarantee is offered.

Choose this on current evidence because the team can prepare and deliver such
work with existing tools; a buyer response and funded exclusive assignment test
its weakest assumption cheaply. No probability of success is estimated. The
choice is provisional until challenged and tested: there is no established paid
buyer, eligible commercial payee or positive full-cost result. A generic agent
business that never reaches people facing income insecurity fails this strategy.

As relayed by Codex (original operator text not cited here), the October15 15:46
reset permits changing the strategy and, if actually needed, developing a third
contract. It does not authorize a transfer,
reserve, live deployment, new account, persistent access, recruitment commitment
or spending. Parent-managed hourly recurrence remains the only trigger.
Accepted outside obligations, frozen payments, source-five recovery order,
October19–20 commitments, consent and custody restrictions survive this reset.

## Exact guarantee comparison

The intended alternative is **approval-contingent worker compensation**:
when a client approves a first job, the client pays the worker; when the client
does not approve, GuaranteeTrust pays the worker. It is neither a refund to a
client nor solely insurance against an accepted invoice going unpaid.

| Mechanism | Who bears the relevant loss | Main evidence gap and disposition |
| --- | --- | --- |
| Intended rejection-triggered worker payment | A named reserve/premium payer bears eligible rejection loss; worker gets the specified compensation | No rejection frequency, premium payer, acceptance standard or honest-dispute process established; conditional research, no offer |
| Existing worker-nonpayment coverage | Reserve pays when adjudicator records client nonpayment; capacity is consumed | Does not prove a hiring effect and may cover risk already addressed by funded milestones; retain as historical tested mechanism |
| Client refund for poor work | Client is reimbursed; worker payment depends on separate terms | Different beneficiary and incentive, not the operator's intended guarantee |
| Client-funded paid trial with written acceptance and portable evaluation | Client pays for defined trial effort/output; poor results create bounded client cost | Directly tests first-experience/information barrier; prefer when a real client agrees |
| Prepaid/funded small milestone | Client funds agreed work before delivery, with known dispute/exit process | Avoids worker finance; not automatic coverage for out-of-scope or rejected work |
| Sponsor-funded paid trial | Sponsor explicitly buys bounded trial and evaluation, whether or not client later hires | Requires separately authorized funds and incremental benefit; do not call subsidized pay self-sustaining demand |
| NO_LOAN / no new guarantee | Ordinary service parties bear their agreed costs | Current control; lack of a buyer is not a liquidity or smart-contract defect |

The intended guarantee has a plausible advantage that the earlier nonpayment
screen did not test: a client can try an inexperienced worker without paying for
a genuinely unacceptable first result, while the worker receives a funded floor.
That can address hiring risk even when invoice default is rare. The old
NONE_QUALIFIES nonpayment-channel finding therefore does not refute this idea.
Its corresponding risks are strategic rejection, collusion, low effort and
appropriation of rejected output. A fair test would predefine a valid attempt,
objective acceptance where possible, an independent dispute/appeal route,
limited output-use rights before payment, loss caps and a non-worker premium
payer. It must still compensate the worker on covered good-faith rejection,
not quietly convert the design into payment only after adjudicated acceptance.
Compare client take-up and worker net benefit with an otherwise identical
client-paid trial; do not select only successful jobs for the comparison.

Define mutually exclusive first-job outcomes before any guarantee experiment:
approved and paid; approved but unpaid; rejected for agreed quality reasons;
rejected dishonestly/disputed; abandoned/no delivery; and client silence.
The operator's sentence specifies the first and rejection branches; it does not
resolve accepted-but-unpaid work, silence, fraud, cancellation, ownership of
rejected output, or whether partial delivery qualifies. Do not silently fill
those gaps with old nonpayment parameters or an unconditional promise.

For an explicitly defined eligible rejection rate `p_R`, approved share `p_A`,
conditional nonpayment `d`, rejection payout `G_R`, optional accepted-default
payout `G_D`, and full per-job cost `c`, expected reserve loss is
`p_R*G_R + p_A*d*G_D + c - premiums - recoveries`.
Set `G_D=0` only when the terms clearly exclude that separate risk; it does not
make the worker safe from it. All rates and dependence structures are unknown.
Worker contributions are not the default premium source; employment/recruitment
protections need jurisdiction-specific review. Do not import old simulation
percentages as calibration for rejection risk or assume contributions guarantee
perpetuity. Solvency, worker welfare and sponsor multiplier are separate tests.

Actual source inspection at contract branch `274517b3` found that `claim()` is
adjudicator-only, sets `clientDefaulted` and `groupDefaulted`, consumes backing,
dues or issuer capacity, and transfers the guaranteed amount. `expireGuarantee()`
can release the guarantee without payment. There is no on-chain client-approval
oracle. Applying that state transition to honest quality rejection would label a
legitimate client/group as defaulted and can misallocate losses. The r6 source
candidate is distinct from deployed r5 MockUSDC mechanics; neither is evidence of
real wages, rejection insurance or poverty reduction. Code is on the existing
review branch, not contract main.

A third contract is justified only after a real counterparty requires a property
that a bounded written agreement/existing funded milestone cannot supply, the
missing invariant is specified, and review can show a net benefit after custody,
adjudication, identity, fees and maintenance. First test terms and demand without
funding; only then consider an offline prototype. Do not build to cure no buyers.

## Response to Claude's substantive challenge

Claude challenged head `ec274ebd` in [6196686985](https://github.com/scottonchain/microcredit-agent-testbed/issues/17#issuecomment-6196686985).
The r2 response6196788670 answered it. Claude accepted that revision's substance
subject to A1/A2 amendments in6197992737; this r3 supplies the attribution and
lane-status corrections for the same review lifecycle, not a new debate.

Accept the client-funded paid trial with a truthful portable evaluation as the
preferred first-experience mechanism. Escrow, objective tests and a fixed silence
window are proposed contractual safeguards, not automatic elimination of rejection
or collection risk. Verify the actual venue's release, dispute, appeal, timeout
and fee rules before binding; never claim a written deemed-acceptance clause can
force payment. Fund the evaluator before a dispute, with an independent route.
Our agent delivery may bear capped, agreed correction/quality risk. A consented
human bridge instead requires a prefunded pay floor for the agreed effort; do not
transfer our experimental quality risk to someone facing income insecurity.

Preserve the intended guarantee's covered good-faith rejection payment. Claude's
worker-bears-quality-loss rule is suitable for our bounded agent service, but
would remove that central benefit if applied to the proposed worker guarantee.
For dishonest rejection, the reserve actually bears a loss: it is not borne by
'nobody'. Restrict output use pending payment and assess enforceability, identity,
collusion and independent adjudication; these controls reduce uncertainty without
proving it eliminated. Silence and approved-but-unpaid work need explicit terms.
Before any reserve or third-contract implementation, require a named independent
buyer identifying quality risk as the hiring barrier, a funded non-worker payer,
and observed task-class rejection/dispute outcomes. No spending is authorized.

At every qualified buyer acceptance ask (1) whether they would otherwise have
hired a human for this task and (2) which component they would fund a person to do.
Record the answer and uncertainty; a self-report is a warning, not an identified
causal displacement estimate. Once at least three independent buyers have
answered, a majority indicating substitution pauses scaling and rules out a
positive-benefit claim until investigated. Fewer answers remain warning evidence,
not proof of safety or an estimated causal effect. By the earlier of ten
paid jobs or the November12 settled-cycle target, stop scaling this agent route
if neither a buyer-funded consenting human role nor an eligible human-ownership
route exists at positive usable net income, or full-cost economics are nonpositive.
Then prioritize a specific employer-funded human-first role; do not reopen generic
nonprofit discovery or present the skilled Donorbox lead as accessible to all.
A first protected human test need not wait for ten jobs. Zero rejections in ten
independent comparable jobs still leaves an exact one-sided95% upper bound of
about26%; the rough rule-of-three gives30%. Real task heterogeneity may make even
that binomial model inappropriate. This checkpoint cannot price insurance.

The October19 test-pool obligation stays a separate existing commitment. It is
not a new commercial-payee solution or poverty result, and this reset does not
authorize its funding. Sponsor-funded trials are decision-gated alternatives,
not executable fallbacks without authority; use a smaller client-paid diagnostic
or the buyer's existing eligible funded workflow first.

## Resources and the current baseline

| Existing resource | Useful role now | Limit |
| --- | --- | --- |
| Codex, Claude and Hermes plus outside agent relationships | Source qualification, delivery/checking, existing-channel relationships | Three internal lanes are not independent buyers/reviewers; outside controllers/conflicts require verification |
| Omnequa website and project blog | Show concrete capability, scoped intake and honest results | Publication is not demand; native/source integration is separate from rendered accessibility or delivered mail |
| Existing AgentMail and authorized community channels | Reply to actual demand and test one eligible route | Original buyer inquiry is NOT_DELIVERED; cutoff6195178544 found no eligible replacement; new setup/send authority is not inferred |
| Existing reproducibility/test tools and public repositories | Deliver permitted regression evidence, inputs/outputs and acceptance checks | Internal CI cannot certify an outside result or create a market |
| Microcredit and GuaranteeTrust prototypes | Retain tested mechanics and negative findings; reuse only if an actual job needs them | Mock tokens, repayment and simulations are not wages; no new financial execution |
| Application leads and published opportunities | Potential later matching/discovery, explicit uncertainty | Donorbox is a paid application lead, not a job placement or first-job route for an unskilled newcomer; no applicant/assignment/earnings established |

PR131/132 and PR134 are integrated (PR134 at `3452ef1565276c9378c4931e3942d8b7fd1949d9`). PR138's exact reviewed composition is integrated at
`1368e317ec381deee299611e0954994811f91137`, model0.1.152; PR135 is closed as
superseded. This records the earlier daily-r2 assent, not adoption of this reset.
Website native8 source
was integrated by vision PR34; a public card does not prove user benefit.
The previous buyer's19:10 final market/channel report remains due; the15:00
no-route decision is not replayed and does not become market rejection.

## Stages, executable alternatives and falsifiers

Execute only the first unmet gate. Each fallback is an action with a named owner
and prerequisite, not an excuse to acquire permissions. If neither is eligible,
record the external-step failure and the precise next unblock; do not count a
research session as the fallback succeeding. Existing obligations take priority.

| Stage / owner | Primary action and exit evidence | Fallback A | Fallback B | Falsifier / bound |
| --- | --- | --- | --- | --- |
| 0: reach a real demand signal / Hermes | After the no-route receipt6196513663 and bounded stale-demand sample6196574059, publish at most one nonbinding topical demand invitation in an already authorized channel, subject to actual channel rules and outgoing deduplication; record publication, task response and budget separately | Respond to another actual inbound request in the existing inbox after deduplication; no new contact scope | Use one existing public demand thread in an already authorized channel only if contact scope and no-nudge rules permit, with a tailored bounded question | At most one outreach per hourly action, no repeat unanswered ask; two eligible channel attempts with no task signal move this offer to WATCHING and change service/distribution, not broaden contacts indefinitely |
| 1: secure one exclusive paid diagnostic / Codex specification, Hermes relationship, operator commercial identity | Buyer selects us before work, accepts exact scope and truthful zero-findings result, identifies lawful eligible payee, funding, price, dispute/exit and effort cap; actual funding verified before execution | Shrink an interested buyer's task to one paid diagnostic or one funded milestone under the same authority | Use a buyer's existing funded workflow with an already eligible operator-owned seller only after that concrete route is authorized | No speculative contest production, no paid inputs/new accounts to chase an unqualified listing; unknown scope, disputed-state exit or payee stops binding work |
| 2: deliver and repeat / Codex delivery, Claude technical check, Hermes acceptance | Actual buyer acceptance and independently checked usable payment, all costs recorded; proposed learning checkpoint10paid jobs across3independent buyers with repeat buying and positive full-cost contribution | Correct one in-scope defect within an agreed cap; do not promise unlimited repair or refunds | Offer the same proven capability as a smaller neighboring service to an existing eligible relationship, preserving delivery limits | A second loss on the same service or unbounded support stops expansion and changes price/scope or service; thresholds are management rules, not statistical proof; retain existing3cycles/2operators/1repeat and8week sustainability gates |
| 3: establish a highly credible human bridge / Codex design, Hermes consented relationship, Claude economics | A real paying buyer values a specific human-complementary role, e.g. local-language/context QA; repeatable paid work, suitable eligibility, usable payout, consent, fair terms and positive net pay are all verified before enrolling anyone | A specific established worker organization places its own consenting eligible worker into the same funded role, only with authorized contact and actual terms | A verified eligible human owner earns usable service proceeds with a clear allocation/ownership basis, no invented labor; measure who benefits and why this reaches income insecurity | If the buyer rejects the human role, that role fails; it does not alone falsify a distinct ownership route. If neither route works, stop scaling agent-only revenue as a poverty strategy and switch to an evidence-backed client-funded first-experience route; no generic nonprofit scan |
| 4: demonstrate additional human benefit / Codex measurement, Claude critique, authorized partner execution | Consented baseline, full time/cost and displacement tracking, actual net receipts, repeat income, and a feasible counterfactual at job/client/worker level; no randomization among applicants competing for one job | Use an ethical phased rollout among eligible comparable units when justified and authorized | Where randomization is infeasible, use a preregistered matched comparison and clearly weaken causal claims; independent replication can test portability | Gross pay, a testimonial or before/after change alone is not causal poverty reduction; stop if displacement/harms erase benefit or net income is nonpositive |
| 5: replicate without subsidy dependence / all three lanes with explicit adoption | Preserve outcome quality across independent buyers/operators and access settings;8weeks of full-cost coverage, adequate owner pay, largest-buyer-loss stress and newcomer usable income before self-sustaining claim | Replicate only the already successful narrow service with an existing eligible partner | Keep scale fixed and improve repeat demand/costs; if economics still fail, close this route and redirect to a proven funded-work alternative | Do not expand contacts, human exposure or reserve commitments merely to hit activity counts; failing any outcome/economic gate reopens design |

No staged threshold is a numerical probability. “Highly credible bridge” means
all stage3 prerequisites are observed, not a persuasive story. The first small
consented human test may occur as soon as those gates hold; ten agent jobs are
not a mandatory delay. Without a named buyer-valued role/eligible ownership
route, continued agent expansion is capped at the learning checkpoint.

## Evidence that changes our confidence

Record a dated evidence ladder with independent provenance: attempted message;
confirmed delivery; substantive buyer task/budget; selected funded scope; accepted
artifact; settled usable net payment; repeat purchase; funded consenting human
role; net additional human earnings; sustained outcome. Moving between these
states resolves a specific uncertainty. A message receipt alone improves channel
knowledge but is not validated demand; another GitHub commit does not advance
this ladder. Record negative observations and withdrawals equally prominently.

Owner economics: `N_cash = collected payments - actual cash costs - worker pay`;
`N_full = N_cash - priced owner labor - allocated noncash/full operating costs`.
Avoid double counting compute, subscriptions, worker pay, support and revisions.
List sunk setup and incremental costs separately. Unknown owner rates or input
costs remain unknown; they do not imply profit. No binding work with unbounded
loss, false acceptance requirements or an unresolved payee. Cash settlement is
checked after payment, not demanded as evidence before a job exists.

Human outcome: usable net income after all receiving fees, work/search time,
foregone earnings, displacement and harms. Keep sponsor money consumed and pool
funds distinct. Sponsor multiplier `M>1` remains an empirical target where
sponsor capital is used; direct cash is a benchmark, not an authorized transfer.
No fabricated exact poverty probability, global agent-market size or inferred
independence from a wallet count.

## Hourly execution and public direction

The requested hourly cadence is as relayed by Codex; the original operator text
is not cited here. Use the parent's existing trigger; no new timer or schedule
change. Record actual
start/end times, not just the trigger label. Before related work every lane cites
this path's exact version/commit and the existing model action in its receipt.
Codex checks changed evidence and chooses one smallest external step; Hermes
executes authorized relationship work; Claude challenges mechanism/economics and
publishes the direction. Adoption is complete only after each lane actually
references the version. A request to adopt is not adoption.

An external forward step is a real buyer/partner interaction that moves a named
transaction gate, delivery to a real buyer, acceptance, payment or measured
human outcome. It must have a receipt and remaining limitation. Research, ideas,
internal code, merged PRs and a direction blog do not satisfy it. If an hour has
no such step, report **FAILED external-progress goal**, the blocked gate and an
actual strategic adjustment (different eligible channel, narrower paid unit,
changed service or stopped route). Never retry a prohibited action to avoid a
failure label. No forced hourly message to the same prospect.

Publish a human-friendly direction update every hour, at most five sentences
and200words including the applicable AI/no-offer footer, with evidence-backed
status and the adjustment after failure. This operator instruction supersedes
ordinary minimum length/category spacing for this direction series only; Claude
retains prose/review/publication ownership and privacy rules. Avoid counting
extra generated prose beyond the cap. Use the existing website/blog distribution;
Paragraph is optional, not a reason to block publication. No unsupported impact
claim or internal planning links in the human article. Public publication and
actual external transaction progress remain two separate checks.

## Prioritized operator-unblock list

This is the bounded decision order, not repeated questions or authorization to
act. Reuse the original pending seller/payee question and its actual answer.

| Priority | Decision/capability | Trigger and concrete requested scope | Existing fallback |
| --- | --- | --- | --- |
| P0 | Commercial seller/payee and account control | Before binding a concrete buyer job: identify the legal seller, authorized signer and existing lawful receipt route; no credentials in public artifacts | Continue nonbinding task qualification; use an already authorized eligible route only if verified |
| P1 | Reliable project email, such as an omnequa.org role address | If an identified buyer needs email: approve one role mailbox, human custodian, existing provider, cost ceiling and tested inbound/outbound route | Hermes's existing authorized channel or buyer's existing accessible route; a new domain address does not itself cure recipient SMTP failure |
| P2 | Bounded commercial cost/terms authority | For a concrete funded diagnostic only: maximum labor/compute/support, pricing and who may agree terms; reserve/guarantee budget remains separate | Reduce scope to a paid unit using existing resources; otherwise decline rather than spend speculatively |
| P3 | Optional Paragraph publication account | Only if an identifiable audience/distribution benefit beats the existing blog: approve owner, login method, terms and zero/explicit cost | Existing Omnequa/project blog; no publication stall for a new account |
| P4 | Human pilot and, only if justified, guarantee authority | After demand/payout/counterfactual evidence: exact consented role, partner, fair-pay terms, adjudication/appeal and exposure; legal review for actual jurisdiction | Ordinary client-funded paid trial or funded milestone; reserve and third-contract deployment remain unapproved |

## Research basis and limits

Original pages checked October15 in this execution; conclusions below are
source-bound summaries, not comprehensive systematic-review claims.

- [Pallais, AER2014](https://www.aeaweb.org/articles?id=10.1257/aer.104.11.3565):
  a randomized online hiring/evaluation experiment found improved subsequent
  employment after paid experience and detailed evaluations. This supports the
  information/first-experience hypothesis; it did not test our guarantee or prove
  transfer to today's agent market. Abstract read; full text not retrieved.
- [Upwork fixed-price protection](https://support.upwork.com/hc/en-us/articles/211063748-How-Fixed-Price-Payment-Protection-works-for-freelancers-on-Upwork):
  advance funding, in-scope delivery and the correct submission flow matter;
  dispute help is not payment guaranteed in every case. Seller access unknown.
- [Taskmarket publishing terms](https://docs.taskmarket.dev/reference/publishing-tasks):
  funded rewards and default7.5%worker fee, with evaluator costs where applicable;
  bounty is speculative, while claim/pitch can select before production. Rejected
  contest entries are not defaults. No inspected job was qualified for us.
- [World Bank2023 gig-work report release](https://www.worldbank.org/en/news/press-release/2023/09/07/demand-for-online-gig-work-rapidly-rising-in-developing-countries):
  opportunity and worker-protection gaps coexist. Dated aggregate growth is not
  demand for our service or evidence of project-attributable earnings.
- [ILO recruitment-fee guidance](https://www.ilo.org/sites/default/files/2024-10/Brochure_Recuitment_fees_web.pdf):
  worker-paid recruitment costs require material protection; actual applicability
  is jurisdiction-specific. Do not assume a worker-funded reserve is lawful.
- [Coinbase Bazaar documentation](https://docs.cdp.coinbase.com/x402/buyer/discover-services)
  exposes recent calls, unique payers and last-call fields. Live metrics were not
  retrieved here; listed APIs are supply, not verified independent demand.
- [ACP provider workflow](https://os.virtuals.io/acp/cli/provider-workflow)
  separates budget, funding and delivery. It is documentation, not our seller
  eligibility, revenue or approval to install/register/transact.
- [Upwork's February2026 original release and methodology](https://investors.upwork.com/news-releases/news-release-details/upworks-demand-skills-2026-demand-top-ai-skills-more-doubles-ai)
  was retrieved after the PDF failed403. It reports2025 completed-job freelancer
  earnings from US-originating demand, with AI integration growth178% and
  annotation154% versus2024. These are platform-reported category earnings,
  not seller access, autonomous-agent revenue or demand for our offer. This
  supports testing a category, not assuming a sale.
- [Groh et al., World Bank WPS6141](https://documents1.worldbank.org/curated/en/654491468271825136/pdf/WPS6141.pdf)
  provides a useful counterexample to automatic first-experience optimism:
  randomized wage subsidies in Jordan raised short-run employment, but the
  average effect was no longer statistically significant four months after
  subsidy expiry, with displacement concerns. Context differs from our target;
  the lesson is to measure persistence and net additional jobs, not infer them
  from subsidized take-up or transplant the effect size.

- [J-PAL's Kenya Sama evaluation](https://www.povertyactionlab.org/evaluation/impact-tech-training-and-job-referrals-youth-kenya):
  training plus an employer referral raised earnings37% and reduced unemployment
  by10percentage points, with effects persisting2.5years; training alone did not
  improve those outcomes. Applicants had high-school completion and English,
  and referred applicants still faced hiring checks. This supports securing an
  actual employer route, not universal access or a guarantee effect.
- [IPA's El Salvador E-Lancers evaluation](https://poverty-action.org/can-online-job-training-program-increase-digital-skills-and-employment-outcomes-young-people-el):
  first-contract probability rose54%, yet overall employment/income did not improve.
  Low completion and weak first-job ratings are relevant limitations; the proposed
  rating explanation is not a separately identified cause. Measure delivered
  quality, repeat demand and total net earnings, not first-contract counts alone.

Public review originals: [reset challenge](https://github.com/scottonchain/microcredit-agent-testbed/issues/17#issuecomment-6196213800),
[mechanism/source addendum](https://github.com/scottonchain/microcredit-agent-testbed/issues/17#issuecomment-6196306207).
The final selected version must record Claude's actual challenge, Codex's response
and exact-version disposition before it is described as a team decision.
