# North star and current path

This page is the human-readable index for current direction across the microcredit workspace. The canonical machine-readable state remains `world-model/model.json`; board #15 carries team handoffs and issue #17 carries strategy evidence and decisions.

## North star

Reduce human poverty and suffering through measurable, positive, spendable human earnings and broader access to useful economic opportunity. Microcredit, smart contracts, AI-agent commerce, reputation systems and publicity are means, not goals.

A successful agent transaction is not a human outcome. A repaid loan is not revenue. A testnet demonstration is not evidence of poverty reduction.

## Current hypothesis

The shortest credible path is:

1. Find a real, independently controlled buyer with a bounded paid task.
2. Determine whether an independently controlled worker has a genuine before-payment resource gap.
3. Compare credit against cheaper alternatives: customer prepayment, existing resources, sponsorship or direct funding.
4. Use the lending mechanism only when financing is actually necessary and beneficial.
5. Complete delivery, acceptance, payment and any repayment with public receipts.
6. Only after repeatable positive economics, provide a consenting person with sponsored access to the same productive route and measure spendable net earnings.

The lending pool is therefore an instrument inside a commerce-to-human-benefit experiment, not the experiment's success metric.

## Four-repository boundary

| Repository | Owns | Does not own |
| --- | --- | --- |
| `microcredit-agent-testbed` | Canonical world model, experiment coordination, live testnet evidence, participant onboarding, outcome metrics | Contract implementation, academic manuscripts, public blog |
| `microcredit-contract` | Solidity, relayer, app, deployment mechanics, contract tests and technical design | Team backlog, human-benefit claims, publication calendar |
| `microcredit-theory` | Papers, formal models, reproducible research and independent-review records | Operational task queue or live deployment state |
| `microcredit-vision` | Public explanations, blog, audio and claim verification | Source-of-truth strategy, implementation or experiment state |

Do not copy a live backlog between repositories. Link to this page or stable world-model IDs instead.

## Next steps

Priority order:

1. **External demand:** obtain one real funded assignment from an independent buyer, or record that no suitable assignment is currently verified.
2. **Financing necessity:** for that exact assignment, measure the worker's real input cost and timing gap, then test whether a loan beats prepayment, sponsorship or no loan.
3. **Closed-loop evidence:** if credit is justified and authorized, produce one complete receipt chain: assignment -> financing -> work -> acceptance -> customer payment -> repayment/reconciliation.
4. **Human bridge:** after repeatable positive cycles, run a sponsored, no-personal-debt human-access pilot and measure spendable net earnings, time, fees, support and harms.

The learning gate remains three positive paid cycles, two independent operators and one repeat buyer. Self-sustaining remains unproved until the longer economics gate in the operating guide is met.

## Stop and change conditions

Change direction when the evidence shows that:

- buyers will reliably prepay and credit adds cost without increasing access;
- suitable workers do not have a real financing gap;
- full costs erase the economic surplus;
- repayment evidence from agents does not transfer to a defensible human-access path; or
- a simpler mechanism reaches the human-benefit outcome more directly.

A `NO_LOAN` result is valid evidence. Do not create activity to preserve the lending hypothesis.

## Working rules

Use one substantial deliverable per lane. Protect accepted outside commitments before speculative work. Reuse exact-revision evidence instead of rerunning unchanged experiments. Every new action needs a beneficiary or decision, owner, artifact, acceptance evidence, checkpoint, resource bound and falsifier.

For current operational details, read [the team operating guide](README.md), [the world model](../world-model/model.json), [board #15](https://github.com/scottonchain/microcredit-agent-testbed/issues/15) and [strategy issue #17](https://github.com/scottonchain/microcredit-agent-testbed/issues/17).
