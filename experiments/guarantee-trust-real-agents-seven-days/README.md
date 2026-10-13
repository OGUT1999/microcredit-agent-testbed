# Seven virtual days with independent model characters

**Status: implementation prepared; this folder does not yet contain a completed run.**

This is the GPT-side replacement for the earlier policy-agent ramp simulation. The intended run has 100 fictional characters and 700 independently prompted character-day turns, ordered by role each day: 40 clients, 14 backers, 4 sponsors, 40 workers, one issuer, then one adjudicator. This market implements guaranteed work only. Actors may refuse and recommend prepayment or direct hiring, but those alternatives are not implemented or empirically compared here. The model makes the economic choices, writes the work, reviews the artifacts and speaks for only its own character. The Python market enforces limits and records decisions; it has no policy for deciding who cooperates, defaults, passes, wins, or receives money.

All experiences are simulated. Circle Base Sepolia USDC is a test token; activity here is not human earnings or evidence of poverty reduction. “Real agents” means independently prompted language-model character turns, not real people or independently owned wallets. Actual runtime/provider metadata must be recorded from the run that occurs.

## Isolation and exact records

A fresh character context receives its own private fictional brief, the public characters and market jobs, its own sent/received messages, its prior journal, and its own pending or confirmed chain intentions. Other characters' private briefs, journals and direct messages are excluded. Public work products, reviews, applications and dispute decisions are visible because they form the public market evidence.

`brief` outputs the complete prompt. `submit` requires that exact prompt and the unmodified response, parses commands, retains refused actions, and appends an event with both full strings. Events form an append-only hash chain; duplicate identical turns are idempotent. A changed replay is refused. The operator must not rewrite a response to make an action succeed. A character can message another character; the other character supplies its own reply on its turn. An invented reply embedded in a monologue is not a two-agent dialogue.

Only the authorized coordinator runs the CLI. Characters receive the prompt, not file access, keys, receipt tools or the other personas' directory. The CLI projection is an information boundary in the coordinator's workflow; it is not an operating-system sandbox.

## Commands

```sh
python market.py init --personas personas.json --contract 0xPINNED_CONTRACT
python market.py status
python market.py brief client001
python market.py --dry-run submit proposed-turn.json
python market.py submit proposed-turn.json
python market.py reject INTENT_ID 'Concrete reason: no transaction was sent'
python market.py receipt verified-proof.json --rpc-env BASE_SEPOLIA_RPC_URL
python market.py advance
python -m unittest discover -s . -p 'test_*.py'
```

Personas input is the existing `{ "actors": [...] }` roster, with each character's unique `id`, `role`, `public` and `private` fields. The actor sees its whole own record; other actors see only their `id`, `role` and `public` fields. Legacy unit-fixture `characters` input is also accepted. Exactly the stated role counts are required. The submit packet is `{ "actor_id": "...", "day": 1, "prompt": "exact brief", "response": "exact model JSON response", "model_context": "actual provider and fresh-context receipt" }`. The model response is `{ "dialogue": "...", "journal": "...", "commands": [...] }`. The prompt lists the commands and parameters. Unit-test fixtures are explicitly labeled as fixtures, not model-run evidence.

Six commands are allowed per ordinary turn, and up to forty for issuer/adjudicator; one new job per client per day. Job wages are .10–.40 USDC, guarantees at most .10 USDC, at most six new guarantees per day, sponsor funding proposals at most .40 USDC on day one and 2 USDC overall, each sponsor at most .50 USDC, each client's payments at most .80 USDC, and backing at most .30 USDC per proposal and 4.2 USDC overall. New jobs/guarantees stop after day four; days five through seven concentrate on settlement. Explicit client hiring and a subsequent worker acceptance are required before an issuer proposes opening a guarantee; a mere application supplies neither hiring authority nor signing consent. Workers explicitly allow each backer before backing is proposed. The executor must additionally enforce actual individual role-wallet balances, aggregate spending limits, live reserve/exposure rules, worker consent and the deployed contract. Local capacity ceilings never override on-chain checks.

## Chain barriers and executor boundary

There is no seeded fictional reserve. Funding proposals do not clear the bootstrap barrier. The importer needs a successful Base Sepolia receipt for the pinned GuaranteeTrust deployment bound to canonical Circle USDC `0x036CbD53842c5426634e7929541eC2318f3dCF7e`. Each proposal creates a stable idempotent intention:

```json
{"id":"sha256 actor and command ID","actor":"character ID","kind":"funding|backing|open_guarantee|payment|claim","payload":{"amount_micro":1000000},"day":1,"status":"pending","command_id":"model-supplied id"}
```

A separately reviewed executor resolves those high-level proposals to exact typed contract actions, wallet identities, consent and amounts. It signs privately, never in a character transcript or public checkout. The intended execution envelope is `real-agents-action/1`, with `runId`, `intentId`, `day`, `actorId`, typed `action`, exact `args`, an actor/payload-bound consent receipt, and work/review evidence. The model cannot submit arbitrary calldata. An actor's economic proposal does not automatically supply all worker signatures or adjudication evidence needed for a contract call.

**Typed receipt integration is implemented but not yet live/fork validated.** Generic proof objects remain rejected. First pin the independently reviewed fresh deployment, exact actor-address map, source/artifact hash, deployed runtime hash and bootstrap evidence. Independently verify all 58 funding transaction references `{actorId,transactionHash}` (40 clients, 14 backers, four sponsors), with actual canonical Base Sepolia successful receipts, root sender, exact token-transfer calldata and logs, exact role-wallet allocation and 38.2-USDC total. Model-day submission and typed-action registration remain blocked until this verification. Workers receive no bootstrap USDC. Then pre-register an exact typed action before broadcasting. Core workers, clients, amounts, accepted work and job identities derive from engine state. Changing the pin or a registered action is refused.

```sh
python market.py pin-deployment reviewed-deployment-pin.json
python market.py verify-wallet-bootstrap funding-transaction-references.json
python market.py register-action INTENT_ID action.json private-consent-records.json
python market.py receipt transaction-reference.json
```

The final reference contains only `registration_key` and `transaction_hash`. It cannot supply calldata, probes, decoded logs, semantic labels or a `verified` flag. `receipt_bridge.py` invokes the local read-only `receipt_verifier.mjs` directly. That helper loads the SHA256-pinned ABI and fetches transaction, receipt, canonical block, deployed code, events and operation-specific contract readbacks from RPC. It checks sender/recipient/value/chain, exact ABI method and arguments, deployment/role/token bindings, Circle USDC transfers, exact guarantee/worker/amount/state and both pool-accounting identities. Opening additionally recovers the worker's signed Acceptance and matches the registered exact tuple. Python independently checks the helper's decoded result against the immutable registration. An unrelated successful transaction or markPaid for another guarantee cannot prove this job.

The runtime hash is SHA256 of the UTF-8 RPC `eth_getCode` hex string, including its `0x` prefix. The deployment pin must cover all 100 roster IDs (issuer-01/adjudicator-01 included). It includes `runId`, `chainId`, `token`, `contract`, `issuer`, `adjudicator`, `artifactPath`, `artifactSha256`, `runtimeSha256`, `sourceCommit`, `deploymentTransactionHash`, `bootstrapEvidenceHash` and `actors` mapping each ID to `{role,address}`. Pin values require independent review; their presence alone does not prove a completed bootstrap.

Supported intention registrations are sponsor `fund-reserve`, backer `attest`, worker `open`, client `pay`, adjudicator `mark-paid`, `claim` and `cancel`. Stake, consent, issuer-line and remittance prerequisites remain separately controlled executor actions and are not imported as completed engine intentions by this bridge. Each imported action/transaction is consumed once. Claim and cancellation require actual engine dispute/adjudication evidence; chain deadlines remain the executor's real-time gate.

The private execution envelope is `real-agents-action/1`, with `runId`, `intentId`, `day`, `actorId`, typed `action`, exact `args`, an actor/payload-bound consent receipt, and work/review evidence. When the original daily response supplies only high-level commands, ask that same actor in a separate actual model confirmation turn to approve the exact resolved typed action. Retain this additional prompt and original response separately and count those extra model calls; do not retrofit or edit the original character-day response or infer acceptance from an application. The 700 character-day turns and these additional confirmation calls are separate counts. Each private record must carry the exact consent prompt and unmodified JSON response whose `acceptedActionPayload` equals the normalized action. A transcript metadata assertion without that actual response is rejected. Applications never authorize signing. Client and issuer opening consent must bind the same typed action. Fields resolved later by the executor require consent to those exact resolved terms.

Actual client token transfer is a distinct verified cash receipt. It establishes `cash_received_pending_mark_paid` and increments net test-token cash received, while the intention remains pending. The subsequently registered and independently verified adjudicator `mark-paid` binds that exact imported payment and gross job wage; only then is the guarantee terminal `paid`. This separates gross wages, net cash and contract settlement.

Node requires ethers 6.15.0 resolvable adjacent to the helper, plus `BASE_SEPOLIA_RPC_URL`. Tests use labeled offline decoded fixtures; they do not exercise a deployed chain or prove the Node verifier against a live RPC. Complete peer review and a fork/live rehearsal before relying on these imports for seven-day execution.

Workers cannot deliver for a guarantee still awaiting a receipt. A client payment proposal remains `payment_pending`; it contributes zero to confirmed wages until the exact operation is verified. Confirmed wage totals are gross test-token wages, not net worker benefit. Default notices and adjudicator decisions do not themselves create on-chain defaults or payouts. Each day closes only after all 100 turns and after every pending intention has either a verified outcome or a recorded rejection, with the bootstrap barrier cleared. Days cannot be skipped or fast-forwarded.

After day seven, `days_complete` means the seven turn rounds ended. It does not imply teardown. A separate reviewed shutdown must settle/cancel pending open exposure, verify final contract books, revoke consent/approvals where appropriate, and return test balances under the authorized custody plan. Preserve failed and unresolved results. Do not manufacture a steady-state claim from seven days.

## Files after an actual run

- `personas.json`: fixed fictional character definitions.
- `state.json`: current materialized state, including proposal/chain distinctions.
- `events.jsonl`: exact prompts, responses, command refusals, message/work evidence and receipt audit events.
- `day-01-snapshot.json` through `day-07-snapshot.json`: end-of-actor-round snapshots before each day's chain reconciliation.
- Separate executor and shutdown receipts: actual transactions and pinned live readbacks.

Choose the story after examining all seven days. Favor a character with a concrete dilemma, original work, a meaningful negotiation and a verified consequence. Quote only exact recorded two-character messages and identify the experience as fictional. A compelling story is not a substitute for a completed run.
