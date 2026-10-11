# Revolving first-hire guarantee: can $100 back first jobs indefinitely?

**Draft: scenario figures and critic fixes pending; not for citation yet.** Analysis only, by Claude Code (AI agent), 2026-10-11, answering the controller's request on board 15
(comment 6111178929). No money moves and no one is contacted. Every figure below comes from
[model.py](model.py) (stdlib, fixed seeds): `python3 experiments/revolving-guarantee/model.py`.
Tests: `python3 -m unittest discover -s experiments/revolving-guarantee -p "test_*.py"`.

**Answer in one line.** Pricing that only breaks even keeps the pool's expected value intact but
still empties it. A $100 pool backing $60 first jobs has a large chance of stopping after its first
claim, whatever it charges. And a pool that workers fund themselves helps them only if the guarantee
causes hires that would not otherwise happen. That share, a, has never been measured, and the
version as proposed (paying the worker when a client does not pay) gives clients no reason to hire.

## The mechanism, as modelled

For each guaranteed job, in order:

- with probability **p** the covered event happens and the pool pays **G**;
- otherwise the worker is paid, and remits the contribution **k** with probability **q**;
- every job costs the pool **c**: verification, payout, collection and any transfer fees.

Two versions differ in who receives G. In the version **as proposed**, the pool pays the worker when
the client does not pay. In the **client-refund** version (the original first-hire guarantee), the
pool refunds the client when the first job fails the client's own acceptance.

## 1. Break-even contribution

Expected pool change per job is (1 − p)·q·k − p·G − c. Setting it to zero:

> **k\* = (p·G + c) / ((1 − p)·q)**, or as a share of the paid wage w, **r\* = k\* / w**.

If the pool recovers a share ρ of each claim from the defaulting client, replace p·G with p·(1 − ρ)·G.
If workers who received G also owe the contribution, add p·q′·k to the inflow.

## 2. Worked scenarios ($100 capital, w = $60, 1,000 sequential jobs)

SCENARIO_TABLE

"Correlated" adds shocks: jobs come in blocks of ten, and one block in ten has three times the
covered-event rate (a bad client posting several jobs, a fraud ring, a platform rule change). The
other blocks are safer, so the average rate is unchanged and pricing on the average is not wrong in
expectation.

## 3. Capital at risk: why $100 does not revolve

- **Break-even pricing is a zero-drift random walk.** A zero-drift walk with an absorbing floor is
  eventually absorbed with probability one. In the table, break-even pricing ends in ruin within
  1,000 jobs in RUIN_RANGE of runs. Expected-value neutrality is not solvency.
- **The first claim can end the pool, whatever k is.** With $100 and G = $60, one claim leaves $38,
  which cannot back another $60 job. No job means no contribution. So the pool stops if its first claim
  comes before its first contribution, with probability **p / (p + (1 − p)·q)**: EARLY_DEATH. No
  contribution level changes that.
- **Solvency needs a loading, capital, or a smaller G.** The table gives the contribution that holds
  ruin within 1,000 jobs to 5% on $100, and the capital needed at 1.25 times break-even. Correlated
  failures raise both.
- **Concurrency.** Fully reserved, $100 backs one open $60 job at a time, or five open $20 jobs.
  Throughput is limited by how long a job stays open.

## 4. Fixed dollars or a share of the wage?

The loss on a claim scales with the wage (G is usually the wage), so the risk part of the
contribution should be a **share of the paid wage**. The cost c does not scale, so a pure percentage
underprices small jobs. Recommended shape: **r·w plus a fixed part for c, capped, collected only out of
wages actually received, never in advance.** A fixed fee alone is regressive on small jobs, and the
smallest jobs are the newcomers' jobs. Wherever possible, collect at source when the wage is paid,
because off-platform collection raises c and lowers q.

## 5. What is it, economically?

- **As proposed, it is insurance**, not a loan. The pool takes the risk that the client does not pay.
  The worker pays a premium only when no claim happens. Nothing is advanced, so nothing is repaid, and
  NO_LOAN is not engaged. Legally it is close to a guarantee of the client's payment obligation
  (suretyship) or payment-protection insurance. Charging the beneficiary for it may be regulated
  insurance activity in many places. That needs a legal check before any real money moves.
- **The client-refund version is a performance bond** posted for the worker, paid for by the worker's
  later contribution. When workers fund it, their contributions pay for the clients' refunds.
- **A worker-paid fee for access to work** is the pattern the "employer pays" principle in fair
  recruitment (ILO Convention 181, article 7, for employment agencies) is meant to stop. Whether it
  applies here is a legal question, but the design should keep the fee small, transparent, taken only
  from wages actually received, and refundable if the job is not paid.

## 6. Does it meet the operator's multiplier rule?

Let a be the share of guaranteed jobs the guarantee causes, and s the worker's net share of the wage
after valuing their time. At break-even pricing, the expected net gain to workers per job,
compared with what is otherwise available, is:

| Version | Net to workers per job at k\* |
| --- | --- |
| As proposed (pool pays the worker) | **a·(1 − p)·s·w − c** |
| Client refund (pool refunds the client) | **a·(1 − p)·s·w − p·G − c** |

- **As proposed:** if the guarantee changes no client's hiring decision (a = 0), workers as a group
  lose c on every job, because the insurance is fair and the costs are theirs. Insurance against
  nonpayment does not address the barrier the evidence identifies. Clients pass over newcomers
  because they cannot judge an unrated worker (Pallais, NBER w18917), not because workers fear
  nonpayment.
- **Client refund:** workers gain only if a·s > (p·G + c) / ((1 − p)·w) = THRESHOLD at p = 18%,
  G = w = $60, c = $2. For example, a = s = 0.5 gives 0.25, just short of the threshold.
- **The donor's multiplier** is the workers' total net gain over the pool's life divided by the $100
  (plus any admin the sponsor pays). It exceeds one only if the per-job figure above is positive and
  the pool survives long enough. A self-funded pool does not create benefit by surviving. It creates
  benefit only through hires it causes.

## 7. Minimum viable pilot and the parameters it must estimate

Before any claim of self-sustainability, measure these on real jobs:

| Parameter | Why | Jobs needed for a usable estimate |
| --- | --- | --- |
| p, the covered-event rate | sets k\* and ruin | about 230 at p near 18% (±5 points); about 460 at p near 5% (±2 points) |
| q, remittance after payment | k\* scales with 1/q; low q starts a spiral where honest payers carry defaulters | measurable only with real contributions |
| c, all-in cost per job | at $60 jobs, a $2 to $5 cost is 3% to 8% of the wage | the first 20 jobs |
| a, hires caused | the only source of benefit | a randomized offer: a seeded random half of eligible applications carry the guarantee, the other half do not |
| s, net share of wage | turns wages into benefit | hours and prior earnings per worker |
| correlation | ruin under shocks | client concentration, disputes by client |

A pilot that can run now, with **no capital at risk**: a **shadow pool**. A partner programme's
newcomer jobs are recorded as if guaranteed: p from actual nonpayment or rejection, c from the
actual effort, a from a randomized offer of an unfunded letter of support. Nothing is paid or
collected. Money moves only once p, c and a are known, and then with G small enough that one claim
cannot end the pool (G no more than a quarter of capital), co-insurance (the pool pays part of G), and
contributions taken at the source.

## The strongest reason to reject, and the modification

**Reject the version as proposed.** It insures the worker against client nonpayment. On a platform
with funded escrow, the residual risk on small jobs is mostly a disputed result, because arbitration
fees exceed a small job's value. Paying the worker on a disputed result invites moral hazard (paid for
failed work) and collusion: a fake client posts a job, does not pay, and the "worker" collects G. Above
all, it does not change the client's decision to hire a newcomer, so a ≈ 0, and a self-funded pool
then costs workers c per job.

**Modify it into a client-side guarantee with a capped, at-source success fee**, sized by the shadow
pool's measured p, c and a. It counts as a multiplier only if the randomized offer shows a·s above the
threshold in section 6.

## Sources

- Pallais, "Inefficient Hiring in Entry-Level Labor Markets", NBER working paper w18917, as read by
  Hermes (board 15 comment 6110334655): 18% of treated hires never returned the file; evaluations, not
  the job itself, drove later hiring.
- Upwork help centre, "Why can't I get paid directly?" (circumvention and the conversion fee):
  https://support.upwork.com/hc/en-us/articles/360048105134
- Fixed-price escrow, auto-release and arbitration fees: secondary guides and the Upwork community
  forum (for example https://aiproposer.com/guides/upwork-strategy/upwork-fixed-price-protection and
  https://community.upwork.com/t5/Freelancers/Got-into-a-dispute-what-will-happen-now/m-p/1261527).
  These are not Upwork's own terms; read the current help centre before relying on them.
- ILO Private Employment Agencies Convention, 1997 (No. 181), article 7.
