# North star and current path

This page is the human-readable index for current direction across the microcredit workspace. The canonical machine-readable state remains `world-model/model.json`; board #15 carries team handoffs and issue #17 carries strategy evidence and decisions.

## North star

Reduce human poverty and suffering through measurable, positive, spendable human earnings and broader access to useful economic opportunity. Microcredit, guarantees, smart contracts, AI-agent commerce, reputation systems and publicity are means, not goals.

A successful agent transaction is not a human outcome. A repaid loan is not revenue. A testnet demonstration is not evidence of poverty reduction.

## Multiply what exists; do not donate to it

Operator direction, 2026-10-11: **the path forward must be a multiplier on what already exists, not a donation to what already exists. The team must measurably multiply or improve on what is otherwise available.**

- **The bar.** One sponsor dollar must produce more than one dollar of incremental human benefit, counted transparently and auditably against what would otherwise have happened. A route that cannot plausibly clear this bar does not ask for money.
- **The reference to beat.** Direct cash remains a benchmark, not the active route. The team must measure incremental spendable earnings, displacement and harms rather than count every backed wage as sponsor-created benefit.
- **Two scorecards.** Human benefit and pool sustainability are separate. Replenishment contributions recapitalize the pool; they are not worker benefit.

## Current state — 2026-10-11

The project has four active repositories and a working public Base Sepolia prototype. An outside agent has demonstrated borrow-and-repay plumbing on the test pool, but not repayment caused by paid work. A bounded 20-task developer-bounty sourcing pass produced **0 independently accepted assignments, 0 identified consenting first-job workers with verified payout eligibility, 0 credit-qualified cases and $0 project-attributable human earnings**. Broad developer-bounty sourcing is therefore closed absent changed or inbound evidence.

Broad discovery of 501(c)(3) organizations willing to invest direct time or resources in this project is exhausted. Do not restart generic nonprofit discovery unless a new specific lead or changed condition appears.

The contract and agent network remain resources. Do not create a financing need, force an on-chain mechanism into the next experiment, or treat infrastructure activity as impact.

## Active candidate path: revolving first-job payment guarantee

The active candidate is a **revolving first-job payment guarantee**, distinct from the earlier client-refund first-hire guarantee.

The earlier candidate refunded a **client** when a newcomer's work failed the client's acceptance. It insured delivery risk. Preserve that work as prior evidence, but do not conflate it with the mechanism below.

The new candidate protects the **worker** against client nonpayment:

1. An independent client hires a first-time worker for real work and remains obligated to pay the wage.
2. Omnequa guarantees the worker's payment up to a bounded guarantee amount `G`.
3. If the client pays normally, the worker keeps the wage minus an agreed small, capped replenishment contribution `r` to the common pool.
4. If the client defaults or fails to pay and Omnequa honors the guarantee, the worker is paid and owes no replenishment contribution for that failed client.
5. The replenishment amount is calibrated from observed risk, not chosen because a percentage merely sounds small.

This is closer economically to a mutual guarantee or insurance-like pool than to a conventional worker microloan. A client default does not create personal debt for the worker.

### Reserve sustainability

Let:

- `p` = probability of client nonpayment/default;
- `q` = probability the worker actually remits the agreed contribution conditional on the client paying;
- `G` = guarantee exposure;
- `c` = per-job pool cash/administrative cost;
- `r` = replenishment contribution after a client-paid successful job.

Then:

`E[Δ reserve] = (1 - p) q r - pG - c`

and actuarial break-even is:

`r_break_even = (pG + c) / ((1 - p) q)`

Exact expected-value neutrality is **not** enough for a finite pool. Random loss sequences can exhaust a pool even when expected change is zero. Any credible design therefore needs a safety loading above break-even, exposure caps, a reserve floor, correlated-loss analysis, and empirical calibration. Do not claim that a donated $100 "stays $100 forever" until observed evidence supports a much stronger solvency statement.

**Working exposure rules until `p`, `q` and `c` are measured.** The internal theory draft (microcredit-theory, `revolving-first-hire-guarantee/DRAFT.md`, with a reproducible `ruin.py`) simulates a $100 reserve over 500 jobs. Backing $60 guarantees, it runs out 39% to 51% of the time even with contributions loaded 50% above break-even. With the guarantee capped at a fifth of the reserve, it runs out 0.1% to 3.6% of the time. Five jobs sharing one client's outcome raise ruin from 0.3% to 15% to 20%. So: `G` at most a fifth of the reserve, one open guarantee per client, no new guarantee while the reserve is below `2G`, and a safety loading of about 50% on the contribution. The contribution is a capped share of the paid wage, collected at payment or treated as a pledge that is never pursued; it is never a debt.

### Human-benefit scorecard

Do not count every client-funded wage as project-created benefit. The auditable human-benefit multiplier must use incremental outcomes:

`M = (incremental spendable newcomer earnings + measured incremental follow-on earnings - displacement - harms) / (guarantee claims + fees + support/admin + capital-lock cost)`

A replenishment contribution affects the reserve scorecard, not the numerator of human benefit. Before asking for money, the route must state how the counterfactual will be measured and why `M > 1` is plausible. Measure what the guarantee causes by offering it on a seeded random half of eligible jobs or applications. Report sponsor capital consumed (starting reserve minus ending reserve) beside `M`. When contributions keep the reserve level, `M > 1` means the benefit the guarantee causes exceeds what participants and the sponsor pay for it.

## Immediate measurable work

The next work is to make this candidate falsifiable without pretending it is already self-sustaining.

Measure or bound, in the cheapest credible order:

0. **Channel:** where do newcomers face real, uncovered client nonpayment? On platforms with funded escrow that risk is largely covered already, and the documented first-job barrier there is the client's decision to hire, so a worker-side payment guarantee is expected to change little. Qualify a channel (direct clients, small local businesses, late-paid invoices, or a programme placing newcomers with its own clients) with public evidence of `p` before any pilot (`action:qualify-revolving-guarantee-channel-20261011`, Codex, zero spend and zero contact).
1. **Take-up:** does the guarantee change the work newcomers accept, complete and are paid for, and, where clients see it, their willingness to hire a newcomer? Use the randomised offer.
2. **Client loss risk `p`:** what fraction of qualifying accepted first jobs are not paid by the client?
3. **Worker remittance `q`:** after normal client payment, what fraction of agreed replenishment contributions arrive?
4. **Cost `c`:** transaction, dispute, support, administration and payout costs per guarantee.
5. **Exposure and correlation:** how much of the reserve may be outstanding at once, and can client failures cluster?
6. **Human outcome:** incremental spendable earnings, follow-on independent work, displacement and harms.

Use a bounded pilot packet before execution. A $100 pilot can measure take-up, `q`, `c` and behaviour; it cannot estimate `p` precisely or show solvency (a nonpayment rate near 3% needs about 280 jobs to pin down within 2 points). No claim of perpetuity, scale or poverty reduction follows from a model or small feasibility test. Any outreach or reserve needs the operator's own authorization.

Compare this route on every cycle against client prepayment, ordinary payment protection, direct sponsorship, NO_LOAN and any simpler path to the same human outcome. The deployed smart contract is optional infrastructure unless evidence shows on-chain enforcement is needed and better than simpler administration.

If the guarantee experiment is blocked, the controller must not stall. Move the blocked item to WATCHING if useful, take the cheapest available evidence step on the parameters above, or switch immediately to the strongest unblocked north-star action.

## Four-repository boundary

| Repository | Owns | Does not own |
| --- | --- | --- |
| `microcredit-agent-testbed` | Canonical world model, experiment coordination, live testnet evidence, participant onboarding, outcome metrics | Contract implementation, academic manuscripts, public blog |
| `microcredit-contract` | Solidity, relayer, app, deployment mechanics, contract tests and technical design | Team backlog, human-benefit claims, publication calendar |
| `microcredit-theory` | Papers, formal models, reproducible research and internal theory drafts | Operational task queue or live deployment state |
| `microcredit-vision` | Public explanations, blog, audio and claim verification | Source-of-truth strategy, implementation or experiment state |

Do not copy a live backlog between repositories. Link to this page or stable world-model IDs instead.

## Stop and change conditions

Reject or materially modify the revolving guarantee if:

- client nonpayment is high enough that the required contribution materially erodes worker benefit;
- worker remittance is too low for a reasonable capped contribution to replenish losses;
- the guarantee does not causally increase newcomer hiring or earnings;
- displacement or other harms erase the incremental benefit;
- administrative cost, capital lock, correlated defaults or ruin risk require too much capital;
- ordinary payment protection, prepayment, sponsorship, cash or another simpler mechanism produces more human benefit per sponsor dollar; or
- a platform, legal, consent or payout constraint makes the mechanism unsuitable.

A `NO_LOAN` or `NO_GUARANTEE` result is valid evidence. Do not create activity to preserve a mechanism.

## Working rules

At the start of every work cycle, explicitly consider the revolving first-job payment guarantee alongside simpler alternatives. Use one substantial deliverable per lane. Protect accepted outside commitments before speculative work. Reuse exact-revision evidence instead of rerunning unchanged experiments. Every new action needs a beneficiary or decision, owner, artifact, acceptance evidence, checkpoint, resource bound and falsifier.

For current operational details, read [the team operating guide](README.md), [the world model](../world-model/model.json), [board #15](https://github.com/scottonchain/microcredit-agent-testbed/issues/15) and [strategy issue #17](https://github.com/scottonchain/microcredit-agent-testbed/issues/17).
