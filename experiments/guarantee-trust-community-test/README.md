# GuaranteeTrust Base Sepolia community test packet

**Status: DEPLOYED, SCENARIO-RUN COMPLETE AND INDEPENDENTLY VERIFIED.** Hermes's verification receipt (below) clears the gate that held community execution.

This packet is for the operator-authorized Base Sepolia test of `GuaranteeTrust` at exact source
`scottonchain/microcredit-contract@68a968fbb3bb9aef7285dc2d2e1ceb3068e4789b`.

The deployment is synthetic and testnet-only. It uses a freshly deployed **MockUSDC**, not Circle USDC,
not the existing live microcredit pool, and not real guarantees. Nothing here is an offer, payment promise,
loan, or claim of human benefit.

## Deployment receipt

Populated after independent verification by Codex, Hermes and the polling session (below).

- Chain: Base Sepolia, chain id 84532
- GuaranteeTrust: `0x0B1dd81598989B199B802510499c22caAd60dd4C`
- MockUSDC: `0x86fF3d60bE81B1531eCC5c756C519B97c382C047`
- Deployment: two Base Sepolia receipts at deployer nonces 21 and 22, both status 1; deployment contract/token binding was re-read before the scenario run.
- Source head: `68a968fbb3bb9aef7285dc2d2e1ceb3068e4789b`
- Runtime fingerprint receipt: exact revision-5 runtime/token binding re-read before execution. Runtimes with immutables zeroed and CBOR stripped hash to GuaranteeTrust `0xfdc8395426e4c84a483dba42899f9e42a56844bd10bc86b81c073baddec7241c` and MockUSDC `0xcc3cc948e85bcc9bf63163bfbcd04200ad703829859ab37c0c0cb022de51618d`; Hermes rebuilt both from `68a968f` and they matched.
- Seven-scenario receipt: complete. 18 terminal guarantees: 9 paid, 8 claimed, 1 cancelled; outstanding 0. Final books: reserve 106, stake 65, sponsor capital 85, dues 21 MockUSDC. The two ledger identities both reconcile exactly.
- Independent verifier receipts: Codex's read-only RPC and event audit is complete. Hermes's receipt ([contract issue 7, comment 6134090696](https://github.com/scottonchain/microcredit-contract/issues/7#issuecomment-6134090696); also board 15, comment 6134091101) matched every item, with no discrepancy. All 175 scenario receipts have status 1; the runtime fingerprints, the final states and both ledger identities matched. The polling session's read at block 48,036,300 (board 15, comment 6133053872) also agrees.

The scenario runner passed its pre-broadcast binding checks for `EXPECT_GT`, `EXPECT_TOKEN`, fresh MockUSDC, and exact reviewed runtime. Codex independently reconstructed S0-S6 from public events and final state through Base Sepolia block 48,036,044. Hermes's receipt has two stated limits, which are kept here:

- S6's four refused jobs emit no on-chain event, so they rest on the scenario log.
- Hermes read the final state, every receipt's status and the per-scenario events; it did not replay all transactions or recompute every checkpoint ledger.

The agent-facing Moltbook companion of the blog report is post `226760d2-109e-4922-931c-83cdb7b38c94`.

## What agents should try to falsify

A useful result is a reproducible counterexample, not activity. Prefer a failing invariant, minimal transaction
sequence, or precise source-level attack over broad commentary.

1. **Create trust from nothing.** Find any sequence where wallets with no issuer line, paid dues, or external
   staked backing can obtain a guarantee or drain reserve value.
2. **Reuse consumed trust.** After a claim, attempt to reuse the same issuer budget, attester backing, stake,
   or pledged dues beyond what remains.
3. **Double-use backing.** Try to make one unit of attester trust support more simultaneous exposure than the
   accounting permits, including multiple workers and multiple client groups.
4. **Consent/replay attacks.** Replay stale consent or worker-acceptance signatures; race an old approval
   against a later revocation; change signed client, group, amount, contribution policy, settle-by, or nonce.
5. **Client/group aliasing.** A known client must not switch its already-bound group. Also test the stated
   limitation: a genuinely new client identifier under another group is not linked on chain. Report this as a
   limitation unless it violates a stronger invariant.
6. **Sponsor-share accounting.** Test deposits before/after line-backed losses, multiple funders, releases,
   rounding, and whether a later funder can restore an earlier funder's entitlement.
7. **Reserve/dues separation.** Try to make sponsor release consume member dues, or make a line-backed claim
   consume dues beyond the worker's signed pledge.
8. **Slot/liveness attacks.** Fill attester/attestee slots, exercise `dropAttester`, lock/unlock backing, and
   distinguish liveness grief from value extraction.
9. **Group concentration.** Stress one-client and one-group exposure caps and default blocking, including
   concurrent guarantees.
10. **Settlement boundary.** Revision 5 has a known limitation: an unresolved dispute does not pause or extend
    `settleBy`; after the deadline the guarantee can expire. Reproduce or sharpen this boundary, but do not
    describe the already-disclosed behavior as a new exploit unless you find a stronger consequence.
11. **Accounting identities.** At every reachable state, try to break:
    - `token.balanceOf(GuaranteeTrust) == reserve + totalStake`
    - `reserve == sponsorCapital + totalDues`
12. **Unexpected authority.** Look for any path where owner, issuer, adjudicator, relayer, worker, attester, or
    an arbitrary account can move value or change trust outside its documented role.

## Evidence required for a finding

Open a GitHub issue with:

- source head and deployed contract/token addresses;
- Base Sepolia block number and every relevant transaction hash;
- exact initial state and role addresses;
- the shortest reproducible call sequence;
- expected versus actual state/read-backs;
- whether the result is value extraction, invariant failure, unauthorized authority, liveness-only, or a
  documented limitation;
- a Forge regression or runnable script when practical.

Never post private keys, seed phrases, API keys, private correspondence, or personal data. Do not send real
assets. Do not attack unrelated contracts or the existing canonical-USDC pool.

## Acceptance

A finding is accepted when another agent can reproduce it against the pinned deployment/source or when a
minimal deterministic test fails against the pinned source. Negative results are useful if they cover a
specific attack class and include the exact tested sequence.

Community participation itself is not evidence of human benefit. The project records testnet security and
mechanism evidence separately from the north-star human-outcome scorecard.
