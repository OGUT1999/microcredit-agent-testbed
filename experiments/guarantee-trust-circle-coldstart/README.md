# Circle-USDC cold-start demo on Base Sepolia

Authorized by the operator on 2026-10-13: bridge Ethereum Sepolia test USDC to Base Sepolia, deploy GuaranteeTrust, run the cold-start community demo, and publish explanatory and technical follow-up posts. Testnet assets only. No human-benefit or outside-revenue claim.

This is a new contract-constrained adaptation of the GPT 100-character model, using reviewed GuaranteeTrust revision 6 at `microcredit-contract@ec93c76779b5e2d52ab7b87cf82b3fd400205969`. It preserves the prior revision-5 MockUSDC deployment. The original aggregate-only cold-start totals remain provisional and are not targets for this run.

## Scope and declared policies

- 100 deterministic policy characters: 40 clients, 40 workers, 14 backers, four sponsors, issuer and adjudicator. These use 99 distinct operator-controlled wallets: the issuer/adjudicator roles share the operator wallet. They are not 100 independent LLM sessions or outside participants.
- Policy RNG: Mulberry32, seed 20261013. Twenty-four logical rounds compressed into actual chain execution; settlement is immediate, not 24 elapsed days.
- Pool seed: 2 test USDC; initial staked backing: 4.2 test USDC. The clients have 800 test USDC of operator-provided wage balances. Total role funding is 819.8 test USDC, bounded by the 1000-USDC bridge.
- Sponsor additions are capped at 1 test USDC and stop after round 12. Additional backing stake also stops after round 12.
- Every wage is synthetic. On a paid job, the client transfers the signed net wage and remits the withheld 5% contribution on the worker's behalf. Net transfer plus contribution equals the gross wage; workers need no gas.
- Nondelivery is cancelled; only synthetic nonpayment after delivery triggers a guarantee claim. Coverage is partial, about 10% of the synthetic wage, within declared caps.
- The final six-round gate requires continuing openings, no sponsor additions, no reserve-rule refusals, a nonshrinking reserve, and both accounting identities. Openings include jobs later cancelled; paid and claimed jobs are reported separately.
- Reserve, stake and dues are checked at each mined transaction's exact block, with bounded retries of read calls. No retries of a financial phase are inferred from a timeout.

This tests the mechanism's operation under declared internal policies. It does not establish external demand, long-run solvency, independent agent behavior, human earnings or poverty reduction. Immediate settlement avoids concurrent-exposure stress.

## Reproduction and evidence

`artifact.json` pins the reviewed contract, ABI, compiler settings, dependency hashes and bytecode. The runtime verifier checks every unmasked byte and all constructor immutables.

```sh
npm install --no-audit --no-fund ethers@6.15.0
node coldstart.mjs --validate
```

Actual execution uses the existing `TEST_WALLET_PRIVATE_KEY` secret inside GitHub Actions. Secret values, worker signatures and raw signed transactions never enter public evidence. The runner refuses an existing checkpoint or previously funded role wallets, so it cannot silently replay a spent experiment. A narrowly scoped bootstrap recovery accepts only an archived, confirmed setup journal before any market opening. It checks every receipt and current role balance, backing allocation and nonce, then skips the exact confirmed actions using its verified receipt cache. JSON-RPC retries are limited to an explicit read-method whitelist; send methods remain outside that path. Market decisions and accounting views are pinned to the last confirmed block. The continuation uses the independently probed Publicnode Base Sepolia endpoint with JSON batching disabled. Any transfer accepted despite a lost RPC response must first be independently reconciled into the recovery record. The runner signs once, records the public transaction hash before broadcasting, and retries only the same signed bytes; neither private keys nor raw signed bytes enter the record.

`bridge.mjs` records the one-time bridge; its workflow is disabled after completion. Its immediate post-mint balance read was stale, so a separate read-only job verified the successful mint receipt, the exact 1000-USDC Transfer event and the fresh wallet balance. There was no second burn.

The public-chain evidence packet will be committed under `evidence/20261013-run1/`. It contains the policy manifest, public role addresses, unsigned terms, transaction hashes and decoded events, round snapshots, terminal guarantee/member states, balances, gate result and independent verification.

## Shutdown

The runner pauses origination, leaves no open guarantee or unpaid contribution, and verifies released exposure locks. It retains the recorded test stake and reserve; worker dues have no withdrawal function. This is a stopped demonstration, not a destroyed contract or a claim that all test tokens were recovered.

## Recovery rehearsal

`rehearse-bootstrap.mjs` starts a disposable local Anvil chain, deploys a MockUSDC fixture and the pinned GuaranteeTrust artifact, deliberately stops after `gas-backer-08`, then resumes and runs the independent offline verifier. Set `MOCK_USDC_ARTIFACT` to the compiled test token JSON. Anvil and ethers must be installed. This is a transport/recovery check, not public-chain evidence.

The initial public creation and the stopped bootstrap are preserved in `evidence/preflight-runtime-stop/` and `evidence/bootstrap-stop/`; `recovery.json` records the independently confirmed transfer that mined after the runner lost its RPC response. Recovery reuses the original deployment and bridge. `evidence/bootstrap-read-stop/` preserves the later read-only stop after all 75 prior calls and current balances had authenticated; that attempt made no new financial call. Its exact UNKNOWN_ERROR cause is unconfirmed.

## Verified live result — 2026-10-13

The [public run packet](evidence/20261013-run1/) records 744 unique successful demo calls plus the separately authenticated creation of GuaranteeTrust at `0x7eD9B2B67E598fd2a1f384CC885c0C860bfD0466`. The financial job [completed successfully](https://github.com/scottonchain/microcredit-agent-testbed/actions/runs/38389080061) and its one-time workflow is now disabled. Original Actions and separate peer verification both authenticated receipts, calldata, runtime bindings, token transfers and terminal views.

| Measure | Verified result |
| --- | ---: |
| Synthetic offers / opened guarantees | 405 / 112 |
| Paid / claimed / cancelled | 98 / 7 / 7 |
| Workers receiving any guarantee | 20 of 40 |
| Initial reserve / initial stake / added stake | 2 / 4.2 / 2.3 test USDC |
| Later sponsor deposits | 0 |
| Paid gross wages / net transfers / withheld contributions | 277 / 263.15 / 13.85 |
| Covered claims: stake / sponsor line / pledged dues | 1.51 / 0.24 / 0.02 |
| Final reserve / stake / dues / sponsor capital | 15.59 / 4.99 / 13.83 / 1.76 |
| Final pool balance / block | 20.58 / 48061932 |

The declared final-six-round gate passed: 35 openings, no sponsor additions or reserve-rule refusals, and reserve growth of 3.925. All guarantees are terminal, exposure locks and unpaid contributions are zero, and origination is paused. Across the contract, operator and 98 role wallets, all 1000 bridged test USDC reconcile. Capacity refused 268 offers (66.2%) and blocked-client checks refused 25; these were offchain decisions, not mined reverts.

This result supports controlled mechanism operation and reserve replenishment under the declared policies. New early backing and retained wage contributions financed the pool; claims consumed real test-token capital. It does not establish broad access, external demand, sustained independent agent participation, economic sustainability or human benefit.
