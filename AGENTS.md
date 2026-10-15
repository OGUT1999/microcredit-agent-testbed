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

The October15 strategic reset is detailed in [CURRENT_PATH.md](coordination/CURRENT_PATH.md).
Each lane must reference its exact version before related activity. Use its
current review status, buyer-funded next gate, two fallbacks per stage and
hourly external-progress test. The operator's approval-contingent worker-payment
guarantee is distinct from the earlier nonpayment mechanism; no third contract
or financial execution is justified by missing buyers. Preserve historical
negative findings and do not reopen exhausted generic scans without new evidence.

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
