# Microcredit agent entrypoint

Before doing substantive work, read [NORTH_STAR.md](coordination/NORTH_STAR.md), then the current
[world model](world-model/model.json) at a named `main` commit and the shared
[team operating guide](coordination/README.md). NORTH_STAR.md is the concise
human-readable statement of the fixed objective, current evidence state, immediate
measurable experiment and stop/change conditions. The world model is the canonical
machine-readable planning index.

The fixed objective is measurable reduction of human poverty and suffering through
positive spendable human earnings and useful economic opportunity. Microcredit,
smart contracts, agent commerce, reputation systems, publications and the current
deployment are means. Preserve, change or discard them according to evidence. Do
not optimize for transactions, agent activity, repo activity or repayment as ends.

At the start of each work cycle, answer four questions before selecting work:

1. What measurable human outcome or decision does this action serve?
2. What is the cheapest concrete evidence that would move that outcome or decision?
3. Does it multiply what already exists rather than donate to it, and is credit
   actually necessary, or do prepayment, sponsorship, existing resources, direct
   funding or NO_LOAN dominate it?
4. What result would make us stop or change direction?

The active candidate path in NORTH_STAR.md is a revolving first-job payment
guarantee: a sponsor-funded reserve pays a first-time worker if the client does
not pay, and paid workers return a small capped contribution. Every cycle considers
it explicitly, compares it with NO_LOAN, client prepayment or funding and any better
route, and advances its cheapest next evidence (a qualified channel, p, take-up, q,
c, exposure) or switches to the best unblocked action; a blocked test never stalls
work. The lending qualification (NONE QUALIFIES) and the stopped bounty scan remain
evidence and fallback. Broad 501(c)(3) discovery is exhausted; do not restart it
without a new specific lead.

This repo owns agent onboarding, test scenarios, operational checks, experiment
evidence and the team's planning index. Start with `README.md` for the code map,
`ONBOARDING.md` for testnet interaction, and `python tools/check.py` for local
verification. `deployments/current.json` records the live configuration; query the
chain to establish current state.

Coordinate material changes on board #15; use issue #17 for strategy. Ordinary
team communication uses TM2 on that board. Sensitive correspondence follows
`coordination/team-email.md`. Preserve frozen calibration terms, evidence and
outside commitments. Internal agents are not independent evidence and testnet
repayment is not human benefit.

The human-facing entrypoint is the [project blog](https://github.com/scottonchain/microcredit-vision).
Keep agent planning instructions out of human onboarding and public articles.
