# Circle-USDC cold-start policy and packet audit

AI author: Codex. This is a read-only consistency audit of the completed execution
packet, not an additional RPC audit. The packet separately includes successful
online-public-chain-verification of receipts, calldata, token transfers, runtime
bindings and terminal views.

## Exact experiment

- Chain: Base Sepolia, 84532.
- GuaranteeTrust: 0x7eD9B2B67E598fd2a1f384CC885c0C860bfD0466.
- Circle test USDC: 0x036CbD53842c5426634e7929541eC2318f3dCF7e.
- Contract source: ec93c76779b5e2d52ab7b87cf82b3fd400205969.
- Runner SHA-256: b26d3e1e2d50c73710cddfee41e9204d1245bdba03ada453067159c9d36f2372.
- Fixed policy seed: 20261013; 24 compressed rounds.
- Final recorded block: 48,061,932.

The executed runner matches the packet's recorded source hash. The population is
40 clients, 40 workers, 14 backers, four sponsors, one issuer and one adjudicator.
There are 99 distinct wallets because issuer, adjudicator and owner share one
wallet. All characters and funds are internally controlled; independent agents,
external demand, independently earned human income and human benefit are zero.

## Recovery and funding

The 744-row journal contains unique labels and hashes, all with status 1. Its
first 74 rows match the preserved original journal; that archive's SHA-256 is
4df066f72a62c331396d8591837bd60b5dc75125ede658bb4616236e9ef04f78.
Row 75 records the recovered, previously mined tokens-backer-08 transfer at
root nonce 40, hash
0xe64950dfe0720da64fecffbeea0e1e9c9391f39e8ee1242908e1e65bf5e42365.
It appears exactly once. No completed bootstrap funding, stake, consent or
backing call was duplicated.

There are exactly 58 role gas transfers totalling 0.00464 test ETH and 58 token
funding transfers totalling 819.8 test USDC. The initial reserve is 2; initial
stake is 4.2; client prefunding is 800. Sponsors made no later deposit. Backers
subsequently added 2.3 in stake. The initial issuer lines total 1.6, within both
the issuer budget and initial sponsor capital.

The journal's 744 calls exclude the separately authenticated prior deployment
and cross-chain bridge transactions. Its execution-fee total is
0.000673201521073332 test ETH; adding the prior deployment's execution fee gives
0.000702493833073332. Those receipt totals exclude Base L1 data fees. The root's
balance-reconciled execution-window gas cost is separately recorded.

## Outcomes and gate

All counts reconcile across policy events, call journal, guarantees and summary:

- 405 posted jobs = 112 admitted + 268 capacity refusals + 25 blocked-client refusals.
- 112 terminal guarantees = 98 paid + seven claimed + seven cancelled.
- All 98 paid guarantees were remitted.
- Paid gross wages total 277 = 263.15 net transfers + 13.85 withheld contributions.
- Claims total 1.77 = 1.51 committed backer stake + 0.24 issuer-backed sponsor capital
  + 0.02 previously pledged worker dues.
- Only 20 of the 40 worker characters received any guarantee.

The outcome labels follow the declared policy: unsuccessful delivery cancels;
only successful delivery followed by a nonpayment draw claims. The first
cancellation records a dispute and immediate resolution. It does not test
expiration, a prolonged dispute or enforcement of a zero-hash rejection.

Rounds 19–24 opened 8, 4, 5, 5, 5 and 8 guarantees respectively: 35 total, with
nonzero activity in every round. They have zero sponsor additions and zero
reserve-rule refusal. Reserve increased by 3.925 over the window. Both accounting
identities hold at every round and every recorded transaction. The declared gate
therefore passes without changing its acceptance rule.

## Terminal funds and interpretation

The final state reconciles exactly:

reserve 15.59 = sponsor capital 1.76 + worker dues 13.83

contract token balance 20.58 = reserve 15.59 + stake 4.99

Origination is paused, outstanding exposure is zero, all guarantees are terminal,
all exposure locks are released and no contribution remains unpaid. Contract
funds were retained, not recovered. Across the contract, root and all role
wallets, the original 1,000 bridged test USDC is conserved.

The result supports a bounded claim about sponsor-free continuing operation and
reserve replenishment under these internally funded policies. Capacity refused
66.2% of job offers, and half the worker population never obtained a guarantee.
The 100-character population therefore does not establish broad access. A claim
creates no new worker debt but can consume dues the worker previously agreed to
pledge. Immediate settlements, scripted contributions and synthetic demand do not
establish independent adoption, long-run solvency or poverty reduction.

