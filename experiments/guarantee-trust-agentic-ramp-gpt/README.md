# GPT-side GuaranteeTrust ramp-up demo

**Status: complete. Synthetic agent simulation; no public-chain transaction and no claim of human benefit.**

This experiment follows the structure of Claude's 100-character GuaranteeTrust run as closely as the GPT-side tool surface permits: 100 fictional participants, the same role counts, role-ordered daily turns, heterogeneous goals and temperaments, scarce backing, bounded issuer activity, sponsors that react to observed outcomes, and an evidence-first adjudicator. The difference is the initial condition. Claude's private-fork run inherited a mature state (reserve 106, stake 65, dues 21). This run asks whether a community can climb into a stable operating regime from a cold start.

The 100 characters are: 40 clients, 40 workers, 14 backers, 4 sponsors, 1 issuer and 1 adjudicator. They are autonomous policy agents authored and run on the GPT side, each with its own role state, incentives and stochastic decisions. This is a contract-faithful state-machine experiment, **not** 100 independent LLM API sessions and **not** an EVM execution of revision 5. That distinction matters.

## Iteration 1: zero reserve — fails before the first guarantee

A literal zero-reserve start is a hard deadlock under the contract rule that one guarantee may be at most 20% of reserve. Twenty percent of zero is zero, so no positive guarantee can open. Agent coordination cannot solve that without some external first funding event.

That is a useful bootstrap result rather than an implementation failure: GuaranteeTrust needs a nonzero seed before it can protect its first job.

## Iteration 2: 20-unit seed — passes the steady-state gate

The second run starts with a **20-unit sponsor seed**. Backers begin with small amounts of scarce stake, only a minority of workers have initial backing, and eight workers have tiny issuer lines. The market rejects zero-guarantee hiring, closing the market-layer gap found in Claude's run.

Sponsors do not add money merely because demand exists. Their policies require observed settled work and they stop all top-ups after day 12. The run lasts 24 simulated days plus a shutdown settlement sweep.

### Result

- Jobs posted: **447**
- Guarantees opened: **394**
- Terminal guarantees after shutdown: **381 paid, 13 claimed, 0 open**
- Client wages represented in the simulation: **11,835 units**
- Sponsor additions after the initial seed: **45 units**
- Reserve: **20 → 656.25**
- Final sponsor capital: **45.5**
- Final worker dues held in reserve: **610.75**
- Final stake: **210**
- Total claim amount: **69**
- Refusals: **50 insufficient capacity, 2 reserve-floor, 1 zero-guarantee**
- The accounting identity **reserve = sponsor capital + dues** held at every daily snapshot.

## When did it become a steady state?

The predeclared gate was the final six active days:

1. no sponsor top-up;
2. nonzero continuing guarantee throughput;
3. zero reserve-rule refusals;
4. reserve not shrinking over the window;
5. no accounting-identity failure.

All five passed.

Over days 19–24, sponsors added **0**, the community opened **20.83 guarantees/day on average**, reserve-rule refusals were **0**, the reserve grew by **180.25**, and the remaining capacity-refusal rate was **10.7%**. In other words, the binding constraint had moved away from seed capital and toward who had enough earned or staked trust to support the next worker.

This is the ramp-up behavior the experiment was intended to illustrate: the seed is necessary to start, but by the final window the community is no longer waiting for the sponsor to keep operating.

## Shutdown

After day 24 the market stops accepting new work. The simulator then settles every remaining exposure to a terminal paid or claimed state and takes a final snapshot. The final open-guarantee count is **0**. No persistent key or live-chain state remains.

## What this demonstrates — and what it does not

It demonstrates two mechanism-level points in a GPT-side behavioral model:

- literal zero funding cannot bootstrap this contract;
- a small nonzero seed can, under the tested agent policies, reach a sponsor-free operating regime in which worker contributions and staked backing support continued activity.

It does **not** demonstrate that real humans would behave this way, that clients would supply this demand, that defaults would follow these rates, that 20 real dollars would suffice, or that the mechanism creates human benefit. It also does not replace an exact private-fork run driven by 100 independent GPT model contexts. Those remain separate empirical tests.

Supporting files:
- `daily.csv` — every daily aggregate snapshot;
- `summary.json` — terminal totals;
- `steady-state.json` — the explicit convergence gate and result.
