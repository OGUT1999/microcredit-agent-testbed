# Direct-cash benchmark: decision card and the rule every route must beat

Status: **declined by the operator on 2026-10-11; kept as a reference only.** Proposed by Claude Code
(AI agent) the same day as a temporary failover step. Nothing has been spent and no one has been
contacted.

The operator's reason: a donation of $500 this way yields about 87% of $500 in benefit, and the path
forward must multiply the benefit in a transparent, auditable way, so that $1 of sponsor money yields
more than $1 of benefit. The rule is now in [NORTH_STAR.md](../../coordination/NORTH_STAR.md)
("Multiply what exists; do not donate to it") and `claim:multiplier-not-donation-20261011`. This card
stays as the reference a route must beat, never as a proposed spend.

## Why this exists now

- **Nothing currently qualifies.** At 15:11Z on 2026-10-11 the controller rejected the only Stage A
  pilot task and recorded that "no task currently qualifies" (board 15 comment 6110442594). The
  paid-first-job packet is a blocked scaffold (PR 52), and lending stays NO_LOAN.
- **The written rule.** [NORTH_STAR.md](../../coordination/NORTH_STAR.md) says that when no case
  qualifies, the project should "redirect effort toward the strongest direct route to measurable
  human benefit". It also says direct cash or sponsorship "remains the benchmark".
- **The gap.** No one has turned that benchmark into an option the operator can act on. This card
  does that, so the project always has at least one executable route to human benefit while agents
  keep looking for something better.

## The route

| Field | Value |
| --- | --- |
| Target | GiveDirectly, Cash for Poverty Relief (its flagship programme: one-off transfers of about $1,000 by mobile money to households in extreme poverty in Kenya, Malawi, Mozambique, Rwanda and Uganda, per GiveWell's programme review) |
| Channel | the operator donates through GiveDirectly's own donation page; no agent can perform this act, so it authenticates itself |
| Bounded ask | one decision by the operator: donate amount A, or decline. Proposed A: $480, the cash the blocked pilot would have spent |
| Expected evidence | the donation receipt (kept private) and GiveDirectly's published programme figures |
| Success | the receipt exists; the project then records A and the share GiveDirectly states reaches recipients |
| Failure | the operator declines or defers; that is recorded as a decision, and the agent routes continue under the rule below |
| Fallback | nothing waits on this card: agents keep testing other routes against the same benchmark |

GiveDirectly's 2025 figure for this programme is that more than 87 of every 100 dollars donated
reaches recipients; its financials page also lists 84.8%. Across all its programmes over the past
three years the figure is 67%, lower because disaster response costs more. At A = $480, the expected
cash delivered is about $407 to $418, or roughly 0.4 of one household transfer.

The evidence on outcomes is published, not ours. In Kenya, unconditional transfers raised assets,
consumption, food security and psychological well-being at nine months, and assets were still higher
at three years (Haushofer and Shapiro). In the same setting, a later study measured a local
multiplier of about 2.5 (Egger et al., *Econometrica* 2022). GiveWell rates the flagship programme
at about 3 to 4 times its benchmark, below the 6-times bar it uses for its own grants. It rates some health charities
higher, but those do not produce the spendable earnings that NORTH_STAR names as the goal.

What the project may claim afterwards: the amount given, the date, and GiveDirectly's published
delivery share. What it may not claim: any outcome for a particular household, any role for the
agent network in the transfer, or that the donation tested the project's own hypothesis. **The
agent network adds nothing to this route.** That is exactly why it is the benchmark.

## The rule every agent-mediated route must beat

A route is worth running instead of, or in addition to, the cash tranche only if, per sponsor dollar:

1. it puts at least as much spendable value in the hands of people **at least as poor** as cash
   recipients; or
2. it adds something cash cannot, such as follow-on independent earnings, that is measured and
   closes any gap left by point 1.

Both points are judged with the route's own measured costs, not estimates.

### The paid first job, scored against the rule

This uses the scaffold's cost card (PR 52) and Hermes's reading of Pallais's working paper (board 15
comment 6110334655). Figures are per $100 of sponsor cash:

| Case | First payment only | Plus two-month follow-on earnings (inexperienced hires: $27 to $30 against $10) |
| --- | --- | --- |
| Fees at the cap ($79.78 a person) | $63 to $74 | $84 to $99 |
| Lowest fees ($63.00 a person) | $79 to $94 | $106 to $125 |
| Direct cash (GiveDirectly) | $85 to $87 | n/a |

**What follows from this:**

- **Dollars alone:** the first job can match or beat cash only if the 2010 oDesk follow-on effect
  holds today and the live fees are low.
- **Who receives them:** cash reaches households in extreme poverty. New online freelancers are
  economically excluded from the platform's market, but they are rarely as poor, and platform
  identity, payout and connectivity requirements screen out many of the poorest. A dollar counts
  for more the poorer its recipient.
- **For extreme poverty,** cash dominates the first-job route on current evidence.
- **For economic exclusion,** the first-job route stays plausible: the pilot's market-access goal
  for new workers.

It remains blocked, and only an admissible task can unblock it.

### The next candidate, scored: a first-hire guarantee

The idea comes from PR 52, comment 6110456034. An independent client who already posts entry-level
work hires an applicant with no completed jobs. The client pays the wage. If the work fails the
client's own acceptance, the sponsor refunds the client. The sponsor pays only on failure, so each
sponsor dollar is leveraged by the client's wage.

The table uses a $60 job, the worker's $50 to $59 spendable pay and the $17 to $20 two-month follow-on.
The failure rates are assumptions; Pallais's 18% of hires who never returned the file is one
reference point.

| Failure rate | Sponsor cost per hire | Expected value to the worker | Value per $100 of sponsor cash |
| --- | --- | --- | --- |
| 10% | $6.00 | $60 to $71 | about $1,000 to $1,180 |
| 18% | $10.80 | $55 to $65 | about $510 to $600 |
| 30% | $18.00 | $47 to $55 | about $260 to $310 |

**What this shows:**

- **On paper the leverage is large.** At these failure rates it beats cash several times over, per
  sponsor dollar, for the economically excluded.
- **Two discounts.** The figures are gross gains to the hired worker. If the client would otherwise
  have hired someone experienced, part of the gain is that person's loss. Cash also still reaches
  poorer people.
- **The deciding unknown is take-up:** whether any independent client hires a newcomer because of
  the guarantee. The cheapest test that tells success from failure is a bounded offer to a small,
  named set of clients, measured by signed acceptances.
- **Not yet executable.** That test needs a channel the platform allows and the operator's
  authorization for outreach and the guarantee fund.

### Any other route

Credit to agents or people, a first-hire guarantee, or anything new is scored the same way before it
asks for money: its spendable value per sponsor dollar, who receives it, and the evidence for any
extra effect. A route that cannot state those numbers is not ready to ask.

## Decision for the operator

Recorded: **declined**, 2026-10-11 (`claim:direct-cash-tranche-declined-20261011`). The rule above is
superseded where it is weaker than the operator's bar: a route must now turn one sponsor dollar into
more than one dollar of benefit, measured on checkable records, not merely match cash.

## Sources

- [GiveDirectly financials](https://www.givedirectly.org/financials) and [Cash for Poverty Relief](https://www.givedirectly.org/poverty-relief) (delivery share; read through search results, since the site is blocked from this host)
- [GiveWell: GiveDirectly's Cash for Poverty Relief programme](https://www.givewell.org/international/technical/programs/givedirectly-cash-for-poverty-relief-program)
- [Egger et al., general-equilibrium effects of cash transfers, *Econometrica* 2022](https://doi.org/10.3982/ECTA17945)
- Pallais, NBER working paper w18917, Tables 3 to 5, as read by Hermes (board 15 comment 6110334655)
