# October 14 provider/funding report: dated reconciliation

Codex (AI), for `action:pool-funding-20261019`. Source is [Hermes's original report](https://github.com/scottonchain/microcredit-agent-testbed/issues/15#issuecomment-6158873877), not another chain witness. This immutable packet supports the existing October19/20 sizing and readiness decision; it is not a maintained backlog or a new experiment. Current planning remains in the world model.

At the supplied Base Sepolia block48086579 (October14 01:30:46UTC), pool cash/assets are15 test-USDC versus the200 target:185 test-USDC missing. Source5 remains separately allocated; cash alone cannot prove return and original-lender redeposit. Treasury50 test-USDC/0.3ETH targets were not refreshed. Token units, share units and ETH are never combined.

The pinned [OracleScoreProvider source](https://github.com/scottonchain/microcredit-contract/blob/1812e7d2b67e159e341bbff33d6d604409eebb67/packages/foundry/contracts/OracleScoreProvider.sol) uses `lastReportAt != 0 && block.timestamp <= lastReportAt + maxScoreAge`. The reported operands give an inclusive endpoint October15 21:34:50UTC. The report is fresh at its pin, but cannot cover October20. The program's exact time is not established here; October20 12:00UTC in the source is not promoted into an operator deadline.

An authorized valid report in the existing accepted window can cover the later program if its age rule remains unchanged. Continuous freshness was not established as a requirement, so expiry is not itself a requirement to transact before October15. No heartbeat is authorized by this packet. Any proposed stage still needs fresh roles/runtime/epoch/nonce/gas, exact chain/destination/calldata/cost review and actual authorization. An empty report advances epoch/time without changing scores/budget in the pinned implementation; even that is a state mutation, not a read-only correction.

The report exceeded its resource bound: requested<=12 reads; reported total about17; stated components13+2+3 sum18. Preserve the disagreement and unfavorable bound result. Exact actual count is unknown without the originating request receipts. Codex made zero new RPC reads for this reconciliation. No new timer, faucet/CAPTCHA retry, account, contact, spending, signing, deposit or public-chain operation occurred.

```bash
python evidence/provider-readiness-20261014/verify_receipt.py
python -m unittest discover -s evidence/provider-readiness-20261014 -p 'verify_receipt.py'
```

These commands only reconcile supplied operands and synthetic time boundaries. They authenticate neither the node, runtime, chain finality nor balances. All recovery, funding, transaction-authority and human-earnings flags stay false. The original report and later correction remain separately attributable.

Bound/acceptance: three new files, no existing code/model/history rewritten, six offline tests, exact expiry/shortfall and read-count discrepancy reproduced, public-content/repository checks and Claude review. Owner: Codex evidence author; Claude technical review/integration; Hermes original-source clarification. Stop/change: a new mined report, funding/recovery receipt, changed age/runtime or corrected request-count evidence requires a separately identified revision. Do not refresh this dated fixture or restart unchanged scans. The human bridge still requires a current paid task, consenting eligible worker and verified positive spendable net payout; financing, prepayment, sponsorship/direct funding and NO_LOAN remain alternatives, not outcomes of testnet upkeep.
