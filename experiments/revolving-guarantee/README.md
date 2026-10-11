# Revolving first-hire guarantee: can $100 back first jobs indefinitely?

**Independent cross-check, not the record.** The steward session answered the same request first in microcredit-theory `revolving-first-hire-guarantee/DRAFT.md` (board 15 comment 6111297730); that draft is the record. This model checks its figures and was corrected after an adversarial review. Analysis only, by Claude Code (AI agent), 2026-10-11, answering the controller's request on board 15
(comment 6111178929). No money moves and no one is contacted. Every figure below comes from
[model.py](model.py) (stdlib, fixed seeds): `python3 experiments/revolving-guarantee/model.py`.
Tests: `python3 -m unittest discover -s experiments/revolving-guarantee -p "test_*.py"`.

**Answer in one line.** Pricing that only breaks even keeps the pool's expected value intact but
still empties it. A $100 pool backing $60 first jobs has a large chance of stopping after its first
claim, whatever it charges. And a pool that workers fund themselves helps them only if the guarantee
causes hires that would not otherwise happen: at break-even, workers gain a·w·(s − p) − c per job.
That share, a, has never been measured, and the version as proposed (paying the worker when a
client does not pay) gives clients no reason to hire.

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

| Scenario | p | q | G | c | Break-even k\* (share of wage) | Ruined within 1,000 jobs at k\* | Stops at its first claim, whatever k | k for at most 5% ruin on $100 (with correlated shocks) | Capital for at most 5% ruin at 1.25·k\* (with shocks) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Platform nonpayment, low | 2% | 0.9 | $60 | $1 | $2.49 (4%) | 83% | 2.2% | about $15 to $23, poorly identified ($15 to $23) | $310 ($340) |
| Platform nonpayment, mid | 5% | 0.7 | $60 | $2 | $7.52 (13%) | 89% | 7.0% | none possible | $370 ($460) |
| Failed first job (Pallais 18%) | 18% | 0.7 | $60 | $2 | $22.30 (37%) | 95% | 24% | none possible | $560 ($1,040) |
| Same, weak remittance | 18% | 0.5 | $60 | $2 | $31.22 (52%) | 95% | 31% | none possible | $640 ($1,150) |
| Failed first job, high | 30% | 0.7 | $60 | $2 | $40.82 (68%) | 97% | 38% | none possible | $730 ($1,870) |
| Partial guarantee | 18% | 0.7 | $20 | $2 | $9.76 (16%) | 80% | not applicable | $16.50 ($33.25) | $190 ($330) |

"None possible": the chance of stopping at the first claim alone is above 5%, so no contribution
reaches the target. In the first row ruin is nearly flat in k between about $12 and $22, so a
2,000-run search lands anywhere in that range; it drops to the 2.2% floor once one contribution lets
the pool absorb a later claim, k ≥ 2G + 3c − capital = $23. Do not read the gap between the two
figures in that row as the effect of correlation. The capital figures are stable across seeds. Simulations use 2,000 runs per point; searches are to $0.25 and $10.

"Correlated" adds shocks: jobs come in blocks of ten, and one block in ten has three times the
covered-event rate (a bad client posting several jobs, a fraud ring, a platform rule change). The
other blocks are safer, so the average rate is unchanged and pricing on the average is not wrong in
expectation.

## 3. Capital at risk: why $100 does not revolve

- **Break-even pricing is a zero-drift random walk.** A zero-drift walk with an absorbing floor is
  eventually absorbed with probability one. In the table, break-even pricing ends in ruin within
  1,000 jobs in 80% to 97% of runs. Expected-value neutrality is not solvency.
- **The first claim can end the pool, whatever k is.** With $100 and G = $60, one claim leaves $38,
  which cannot back another $60 job. No job means no contribution. So the pool stops if its first claim
  comes before its first contribution, with probability **p / (p + (1 − p)·q)**: 2% at p = 2% and q = 0.9, 7% at p = 5% and q = 0.7, 24% at p = 18% and q = 0.7, and 38% at p = 30%. No
  contribution level changes that.
- **Solvency needs a loading, capital, or a smaller G.** The table gives the contribution that holds
  ruin within 1,000 jobs to 5% on $100, and the capital needed at 1.25 times break-even. Correlated
  failures raise both.
- **Concurrency.** Fully reserved, $100 backs one open $60 job at a time, or four open $20 jobs (five if c is paid outside the pool).
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
- **A worker-paid fee for access to work.** ILO Convention 181, article 7(1), says private
  employment agencies "shall not charge directly or indirectly, in whole or in part, any fees or costs
  to workers", with exceptions only under article 7(2). If it or the "employer pays" principle
  applies, no worker-borne contribution is compliant, whatever its size or collection method. The
  client-refund version funded by workers is the most exposed configuration, because workers then pay
  for the employer's hiring risk. Whether a guarantor counts as such an agency is a legal question to
  settle before any contribution is collected. The compliant alternative is a reserve funded by the
  sponsor or the client.

## 6. Does it meet the operator's multiplier rule?

Let a be the share of guaranteed jobs the guarantee causes, and s the worker's net share of the wage
after valuing their time. Take G = w, and for the client-refund version case A: the client pays
every wage and the pool refunds the client on failure, so a worker whose job fails keeps the wage.
At break-even pricing, the expected net gain to workers per job, compared with what is otherwise
available, is the same for both versions:

> **a·w·(s − p) − c**

A caused job is worth s·w net of time (counted in every state, because time is spent on jobs that
end unpaid too). On a job the worker would have had anyway, the covered event pays G instead of
nothing. Contributions at k\* total p·G + c. The payouts and contributions cancel apart from c.

- **As proposed:** if the guarantee changes no client's hiring decision (a = 0), workers as a group
  lose c on every job, because the insurance is fair and the costs are theirs. Insurance against
  nonpayment does not address the barrier the evidence identifies. Clients pass over newcomers
  because they cannot judge an unrated worker (Pallais, NBER w18917), not because workers fear
  nonpayment.
- **Both versions:** workers gain only if a > c / (w·(s − p)): 0.10 at s = 0.5, p = 18%, c = $2,
  and 0.074 at p = 5%. The versions differ in a, not in the accounting: a refund to the client acts on
  the hiring decision, insurance for the worker does not.
- **Not in the records:** fair insurance has value to risk-averse workers with little wealth, of the
  same order as c on a $60 job. The multiplier leaves it out because records cannot show it, but it
  is not zero.
- **Sponsor-funded client refund (not revolving):** M ≈ a·s/f + (1 − a) per sponsor dollar before
  costs, with f the failure rate: 1.89 at a = s = 0.5 and 1.44 at a = 0.25, s = 0.5, at f = 18%. The
  (1 − a) part is a one-for-one transfer to newcomers whose work failed on jobs they would have had
  anyway, so M > 1 needs a·(s − f) > c/G.
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
| a, hires caused | the only source of benefit | a randomized offer by job or client (a seeded random half of eligible jobs or clients), never by application, because applicants to the same job compete; report displacement of other freelancers separately |
| s, net share of wage | turns wages into benefit | hours and prior earnings per worker |
| correlation | ruin under shocks | client concentration, disputes by client |

A pilot needing **no capital**, which can start once the operator authorizes contacting a partner
programme: a **shadow pool**. The programme's newcomer jobs are recorded as if guaranteed, giving p
from actual nonpayment or rejection and c from the actual effort. The shadow p is a lower bound,
because without a payout there is no incentive for strategic rejection, fake clients or slack effort.
A shadow pool cannot measure a: an unfunded letter is a different treatment (Pallais found a costless
endorsement had no effect), and a letter that promised a refund would be broken. So a needs a small
funded phase, randomized by job or client, with fraud controls (independently verified clients, one
claim per client), G no more than a quarter of capital, co-insurance and contributions taken at the
source.

## The strongest reason to reject, and the modification

**Reject the version as proposed.** It insures the worker against client nonpayment. On a platform
with funded escrow, the residual risk on small jobs is reportedly a disputed result: arbitration fees
reported on the community forum exceed a small job's value for both sides, and an unresolved dispute
reportedly leaves the escrow with the client. The deciding reason is that it does not change the
client's decision to hire a newcomer, so a ≈ 0, and a self-funded pool then costs workers c per job.
Moral hazard (pay for failed work) and collusion (a fake client who does not pay) apply to both
versions; the client-refund version pays the worker k\* more on a failed job than on an accepted one
under self-funding. Both need verified independent clients and one claim per client.

**Modify it into a client-side guarantee**, funded by the sponsor or the client unless the legal
check in section 5 clears a worker contribution, and sized by measured p and c. It counts as a
multiplier only if a randomized offer by job or client shows a above the threshold in section 6.

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
