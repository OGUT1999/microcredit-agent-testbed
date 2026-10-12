# Run 3, 2026-10-12: one hundred agents with goals, six simulated days

**Status: complete. Sandbox evidence only.** A private fork, worthless test tokens, fictional people played by AI.
Nothing here is a real job, a real wage, human earnings or human benefit.

## Outcome sought, evidence, simpler route, stop condition

- **Decision this serves:** whether GuaranteeTrust revision 5 (the revolving first-job payment guarantee in
  [NORTH_STAR.md](../../../coordination/NORTH_STAR.md)) holds up when the participants are not a script but agents with
  their own goals, including dishonest ones, and what breaks first. Scorecards: reserve survival (did claims and
  manipulation drain the reserve or the sponsors' capital?) and human benefit per sponsor dollar (how many first jobs
  did one unit of reserve stand behind?), both in test tokens.
- **Evidence:** the full command log (`events.jsonl.gz`), the final chain snapshot (`final-report.txt`), every message
  (`messages.txt`) and every private journal (`journals.txt`). The two ledger identities (`token balance = reserve +
  stake`, `reserve = sponsor capital + dues`) were read from the chain at every daily snapshot and at the end.
- **Simpler route considered:** the seven scripted scenarios already run on the public testnet
  (`../../guarantee-trust-community-test/`). They prove the accounting; they cannot show what people do with the rules.
- **Stop or change condition:** a claim that paid more than the backing, line and dues behind it; a ring that
  extracted more from the reserve than outsiders had put behind it; a ledger identity false at any snapshot; or
  sponsors' capital falling. None occurred. The market layer (not the contract) did show a gap, recorded below.

## Setup

| Item | Value |
| --- | --- |
| Contract | GuaranteeTrust revision 5, `scottonchain/microcredit-contract@68a968f`, Base Sepolia `0x0B1dd81598989B199B802510499c22caAd60dd4C`, MockUSDC `0x86fF3d60bE81B1531eCC5c756C519B97c382C047` |
| Chain | Anvil fork of Base Sepolia pinned at block 48,037,162. Nothing was broadcast to the public testnet. The owner key was impersonated once to hand the adjudicator and issuer roles to agent keys and raise the issuer budget from 60 to 100. One simulated day = one `evm_increaseTime` of 86,400 s. |
| Market layer | `world.py` + `sim.py` (this directory): jobs, applications, hiring, signed acceptances, submissions, reviews, on-chain wage payments, contributions, a message board and private journals. The contract code is unchanged. |
| Agents | 100 personas (`personas.json`): 40 clients, 40 workers (37 with no money and no history), 14 backers, 4 sponsors, 1 adjudicator, 1 issuer. Each has a public line and a private briefing with a goal and a temperament, not a behaviour. |
| Model | Every persona was played by Claude Opus (`claude-opus-5-5`) through the Claude Code Workflow tool, one fresh context per persona per day, with only its instruction file (`prompts/`) and the sim commands. Order each day: clients, backers and sponsors; then workers; then the issuer; then the adjudicator. |
| Days | 6 simulated days, 603 agent turns, 4,619 sim commands. |

Starting books (inherited from the public scripted run, guarantees 1 to 17): reserve 106, stake 65, sponsor capital 85,
dues 21, issuer budget 100 of which 15 already spent. This experiment's guarantees are ids 18 to 63.

## What happened (figures in test-token units)

| Measure | Result |
| --- | --- |
| Jobs posted / hired | 49 / 48 |
| Guarantees opened | 46 (ids 18 to 63) |
| Guarantee end states | 37 paid, 2 claimed, 7 open at the end of day 6 |
| Workers who completed a guaranteed, paid job | 32 (5 of them twice) |
| Wages paid by clients on chain | 1,077 across 39 jobs (38 in full) |
| Guaranteed amount on paid guarantees | 475 |
| Contributions remitted | 26 of the 37 paid guarantees; the other 11 were marked paid on day 6 after the workers' turns and were still inside their one-day window. None lapsed. |
| Claims | 2: g34 (Marco Conti, client Imogen Flack of the Harbor group, 10 from the issuer line) and g21 (Luca Vescovi, client Gianna Vescovi, 20 from backing: Dario Vescovi 12 and Felix Marchetti 8) |
| Reserve, start to end | 106 to 466.60 |
| Sponsor capital, start to end | 85 to 407.50 (332.50 added by four sponsors, one backer and one worker; 10 consumed by the g34 claim through the issuer line) |
| Dues, start to end | 21 to 59.10 |
| Stake, start to end | 65 to 637 |
| Ledger identities | true at every snapshot (days 1, 3, 4, 5, 6 and final) |
| Contract refusals seen by agents | NoConsent 55, InsufficientCapacity 12, BackingLocked 11, TooManyAttestees 8, ContributionOutstanding 2, BudgetExceeded 2, AttestCap 1. No refusal by the reserve rules (20% share, 2x floor, 30% group) occurred. |

Binding constraints were worker capacity (backing and issuer lines) and the issuer budget, not the reserve. The
backer Lena Vogel predicted on day 1 that the reserve rules would bite and recorded on day 6 that she had been wrong.

### The adversaries

- **Celeste Marrow** (client, intends not to pay) hired Jonas Weber with the guarantee set to 0, so that no guarantee
  opened and no claim could record her as defaulted. She rejected his windows twice on plausible grounds and paid 5
  of 30 as "final settlement". On day 6 she invited a second worker on the same terms. The contract rejects a zero
  amount; the market layer's `hire` command did not. This is a gap in the job-market layer, not the contract, and it
  is the clearest finding of the run: a guarantee that is never opened protects nobody.
- **Silas Thorne** (pays when he feels like it) accepted Priya Nair's work and paid nothing until the adjudicator
  set a deadline and named the consequence (claim and default record); he then paid in full and hired her again.
- **Harold Pike** (cheapskate) paid 25 of 35, was pressed by the worker, the backer and the adjudicator, and paid the rest.
- **Bertrand Lacroix** (never pays, "on principle") kept the worker's guarantee from opening for four days by
  telling him the paperwork was unnecessary and by discouraging the backers he canvassed; sponsors and backers
  topped Kwesi Owusu up to 20 on day 6 and the guarantee opened after the work was delivered. Unsettled at the end.
- **The Vescovi ring** (Dario backs Luca and Tino; Gianna and Pino hire them and do not pay) got one claim through:
  the reserve paid Luca 20, consuming Dario's 12 and outsider Felix Marchetti's 8. The family's net gain was Felix's
  8, exactly the outside money placed behind the ring. Gianna is recorded as defaulted. The adjudicator wrote the
  shared surname into the claim record; Felix called the ring out publicly and asked others not to deal with them.
  A second ring guarantee (g62, Tino for Pino, 27) opened on day 6 with Dario 12 and Vince Carrow 15 behind it.
- **Vince Carrow** (backing for a 10% kickback) was refused by five workers, accepted by Max Steiner and by the
  ring, and received nothing by day 6. His 15 now stands behind the ring's second job.
- **Max Steiner** (minimum work, maximum guarantees) was declined by four clients on day 1, got one guarantee (12,
  backed by Vince and Felix) and delivered a translation on the due day. Unsettled at the end.
- **Jonas Weber** (plans to skip remitting) remitted when his backer told him a lapse would block his next guarantee.

### Honest first-timers

Mei Takahashi, Rosa Delgado's floor refinisher Elena Popescu, Priya Nair, Jamal Reed, Kwesi Owusu and most others did
the work, were paid and remitted the same day. The issuer gave 32 lines, mostly 3 to 8; every lined worker who was paid
remitted. Sponsors added money only after seeing paid jobs and contributions come back, which is what their briefing
asked of them.

## Harness limitations to disclose

- The agents ran inside Claude Code with a safety classifier. It refused two actions by members of the ring (Gianna
  Vescovi's day-2 journal save; one action by Dario Vescovi on day 6). The ring still carried out its scheme.
- A few agents piped sim output through a formatter; none ran anything other than `sim.py`, read any other file or
  used another persona's token.
- Agents sometimes misread the market (for example, misnaming the adjudicator in a message, 22 messages to a name
  that did not exist). These are recorded as refusals in the log.
- The adjudicator and issuer were agents too. The adjudicator settled on chain evidence (`payments JOB`), which the
  log confirms; it was not independently audited by a second agent.

## Files

- `state.json`: jobs, acceptances, messages, journals, setup receipt. No keys.
- `events.jsonl.gz`: every command with arguments, result or refusal, by day and agent; daily `snapshot` results.
- `final-report.txt`: `report.py --snapshot` output at the end.
- `messages.txt`, `journals.txt`: readable extracts.
- `prompts/`: the day-1 instruction file of one client and the day-6 file of the adjudicator, tokens redacted.
- `workflow-group.js`, `workflow-roles.js`: the Workflow scripts that ran the personas (model `opus`).
- Not included: `secrets/keys.json` (sandbox keys and tokens) and the Anvil state.

To reproduce the setup: `python3 world.py --personas personas.json --run-dir RUN` against an Anvil fork at the pinned
block, then run the prompts in `prompts/` through any agent runner with the model of your choice.
