# Independent safety review — final prepared snapshot, 2026-10-13

**Prepared code only. Not approved for live execution. No actual model turns, public-chain transactions or protocol rehearsal were performed by this reviewer.** Earlier findings are superseded by this current-state review.

## Verified preparation

Thirty-seven Python market/receipt tests pass. Root additionally reports twelve executor offline checks passing. Role refusal, private roster projection, immutable/idempotent command and turn handling, hire acceptance invalidation, declared context metadata, typed-action registration and adversarial decoded receipt checks are covered. Roster contains100 unique fictional characters with the specified role counts; characters see only their own private brief, journals and directed messages. This is coordinator workflow isolation, not an OS sandbox.

Exact pinned Git-object source at `ec93c76779b5e2d52ab7b87cf82b3fd400205969` was read. Its44,124bytes Keccak256 match artifact source hash `0x0b85c291aa5d388a9159d28a52dccbfc4476bbc3b680fc42f85a407cded3debb`. EIP712 constructor domain is `GuaranteeTrust`, version `2`; the ABI Acceptance tuple matches the source's exact typehash fields and order. The earlier apparent hash mismatch came from an extra newline in a scratch copy and is withdrawn.

Source settlement semantics were verified: claim and markPaid are permitted through `disputed ? holdUntil : settleBy`, then reject. SettleBy is a hard end, not a waiting threshold. Latest executor uses this guard plus reviewed mutually accepted virtual payment-due terms. Opening requires at least one real day until settleBy and exact live contribution-policy equality. Default constructor contribution cap is3USDC and remit window14real days; the current bridge/executor cap matches that policy, and the tiny wages make percentage contribution the binding amount. Zero signed groupId normalizes to clientId; current verifier handles that normalization.

## Receipt and authorization architecture

Typed receipt integration now exists in `receipt_bridge.py` and `receipt_verifier.mjs`; the old arbitrary-proof interface remains rejected. The bridge derives parties, amounts and job terms from market intentions and immutable hired terms, requires exact unmodified JSON action acceptance and coordinator-approved records, and requires explicit client/issuer supplemental approvals. Actual wallet bootstrap verifies58distinct transfers totaling38.2testUSDC before registrations.

The production importer launches the Node helper directly from registered expectations and transaction hashes. Helper checks chain84532, successful mined transaction/receipt/block identity, exact source creation bytecode and constructor arguments, deployed runtime outside known immutable references, root roles/token, calldata, exact ABI events and operation-specific state/accounting readbacks. Worker EIP712 acceptance is recovered independently. Receipts cannot be consumed twice. Cash transfer and subsequent markPaid are separate accounting events; gross wage is never inferred solely from a model payment proposal.

Executor enforces0.1USDC maximum guarantee, six new guarantees/day through dayfour, bounded issuer lines, exact approved worker/client/issuer jobs, pre-transfer client/gross/net scope, named remitting parties and unique payment-hash reservation. Broadcasts are single-attempt, preceded by durable intent records; uncertain broadcasts halt for explicit nonce/hash reconciliation rather than blind resending.

## Actual Node helper integration check

The latest Node verifier, with ethers6.15.0, was exercised through an owned local fixture RPC. Correct funding calldata, ReserveFunded event, canonical-token Transfer, exact deployment/runtime/role and book readbacks succeeded. Altering Transfer amount100000→1 failed with `Exact token transfer required`. This exercises actual RPC/ABI decoding, not just Python decoded predicates. It is a mock transport test, performs no EVM execution or signature/funding operation, and provides no public-chain evidence. Its reproducible script is scratch-only `/tmp/real-agent-review-rpc/rehearse.mjs`.

## Remaining requirements before live execution

- Integrate and rehearse market→typed consent→executor→receipt import end to end. Issuer/adjudicator IDs differ (`issuer-01`/`adjudicator-01` versus executor names); adapters must explicitly normalize these and reconcile consent schemas. Auxiliary stake/consent/line/remit action handling also needs whole-run integration coverage.
- Run a genuine EVM/protocol rehearsal covering funding, staking, signatures, backing, opening, net payment, markPaid, remit, virtual nonpayment claims within real hard deadlines, malicious commands, reused receipts, changed terms, interruption/recovery and shutdown. Unit fixtures and mock RPC acceptance do not verify contract execution.
- Establish the real model-call harness and preserve actual runtime/provider evidence for700 fresh character-day contexts, exactly100 each of seven days. Nonempty context metadata is a declaration, not independent proof. Current tests represent zero actual character turns.
- Complete custody and teardown policy. Dayseven pause/reconciliation records open and unremitted positions plus retained stake/dues; pausing alone does not withdraw backing, release sponsor capital, revoke allowances/consent or sweep role balances. Do not label a run fully settled solely because outstanding guarantee count is zero while contributions remain unremitted.
- Verify actual authorized signer/write path and available whole-run gas budget before enablement.38.2testUSDC allocations are below40cap; incremental0.005ETHfee and0.002ETHgas-funding bounds do not establish that seven days and shutdown can finish within them. Preserve unresolved/failure records honestly.

Workflow remains disabled and `marketReady:false` is appropriate. No completed seven-day run, steady state, teardown, human earnings or poverty-reduction conclusion can be inferred from this prepared snapshot.
