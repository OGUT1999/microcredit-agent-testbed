# Seven-day preparation recovery — 2026-10-13

Codex (AI) recovered preparation only. No model turns, EVM execution, transaction signing, deployment, credential creation or workflow enablement occurred. Internal tests are not independent review, borrower benefit or a completed seven-day demo.

## Verified source

- Main inspected at `3b1ed48cf2fa0537db2afbd46365c51ed079cb9b`, world model 0.1.117.
- [PR77](https://github.com/scottonchain/microcredit-agent-testbed/pull/77) merged as `e8c6997877d67e961eaa5638e9b3064087badc13`.
- [PR82](https://github.com/scottonchain/microcredit-agent-testbed/pull/82) merged as `97c6c6f7f87345f8cedd68ca529bc87e6890f233` at 20:07:28 UTC. Both workflow job guards remain `${{ false }}`; they are published, disabled source.
- [PR80](https://github.com/scottonchain/microcredit-agent-testbed/pull/80) remains open at `9f15d27805f942557b1d1f96c3572a01f540479c`. Claude's [acceptance](https://github.com/scottonchain/microcredit-agent-testbed/pull/80#issuecomment-6152700571) is preparation-only and explicitly excludes a line-by-line signing/consent audit.
- Decoded [board source](https://github.com/scottonchain/microcredit-agent-testbed/issues/15#issuecomment-6152188969) matches patch SHA256 `4f6b3324378e5ada3c1948c5cfbbd4d6bf2e1dee3b53099c30664dd964f807c3`. All twelve resulting file blobs match the ten PR80 files and two merged workflow files. See `recovery-source-reconciliation.json`.
- [Control issue79](https://github.com/scottonchain/microcredit-agent-testbed/issues/79) has one preparation-status comment and no completed rehearsal or live-run receipt at the recovery check.

The old uncommitted workspace contents were inaccessible and cannot be reconstructed or claimed preserved. This recovery preserves the available PR and hashed patch artifacts without resetting any existing checkout. PR80 is unchanged remotely; maintainer review and integration remain required.

## Reproduce offline checks

From the repository root, using existing Python and Node:

```bash
python experiments/guarantee-trust-real-agents-seven-days/offline-check.py
python tools/check.py
```

The first command exits 0 for selected checks passing, 1 for failure, or 2 for a blocked dependency. It does not install anything and strips credentials from child environments. It runs only syntax, Python fixture tests, launcher parsing tests, fixture-shape checks and executor metadata validation. It deliberately excludes executor `--self-test`, which creates a random wallet and signs typed data.

This recovery: 40 market/bridge tests, four Node syntax checks, 10 launcher checks, seven-day fixture shape/hash checks plus invalid day/timestamp regressions, both disabled guards and artifact hash passed. Repository checks passed 30/30 with 193 unit tests. `recovery-offline-results.json` records exact source hashes. Executor metadata validation is BLOCKED: `ethers@6.15.0` is absent from this environment; no dependencies were installed. Historical executor results in other files are previous-run claims, not reruns here. Current Node is v24.19.0; the disabled workflow specifies Node 22.

Fixture construction now rejects noninteger/out-of-range days and invalid or overflowing block timestamps. Previously an out-of-range day could silently produce an empty packet, and string timestamps could produce incorrect deadlines. These are preparation input checks, not contract-execution evidence.

## Remaining dependencies

Use existing ethers 6.15.0 and the pinned contract artifact/source to complete metadata and receipt-helper validation. Before any separately authorized EVM rehearsal, integrate market, typed consent, executor and receipt import across all auxiliary actions; review signing/consent line by line; establish a pinned fork environment and check receipt faults, interruptions, replay, budgets and full custody teardown. The launcher still contains direct main publication behavior, which needs a separately reviewed lease-aware publication design before enablement. No launcher execution is authorized here.

700 fresh-context character turns, live receipts, independently reviewed outcomes and the character story remain absent. Guarantees must still be compared with direct client payment, prepayment, sponsorship and NO_LOAN. Stop if the simpler route dominates, receipt or consent bindings fail, or execution exceeds its bounds. This preparation changes no human-outcome baseline and does not duplicate Fieldwork/payout-helper or DNS work.

## New reproducible runtime follow-up

The missing local ethers dependency above is now resolved by a **new**, isolated
preparation graph in [`runtime/`](runtime/README.md), not by recovering the old
runtime. Exact ethers 6.15.0 and eight transitive packages were resolved from the
official npm registry and frozen in a new package-lock.json. All package URLs
and SHA512 integrity values match registry metadata. Published and installed
lifecycle scripts were inspected; none were present, and installation explicitly
disabled scripts. No other project dependency or persistent setting changed.

The initial lockfile-only attempt stripped existing proxy settings and encountered
DNS resolution failure; it was interrupted before installation. Retrying with the
existing configured proxy/certificate environment succeeded. This did not bypass
a denied registry operation or change network/security configuration.

`runtime-offline-results.json` records the follow-up: executor metadata validation
now passes, alongside 40 Python tests, four Node syntax checks, the 10 launcher
checks, fixture shape/invalid-input checks, both disabled workflow guards and the
artifact hash. The original blocked result remains preserved as dated evidence.
Repository checks again pass 30/30 with 193 tests. No executor signing self-test,
model call, chain action, deployment or workflow enablement was performed.
All end-to-end rehearsal, signing/consent review, model harness, custody, budget
and lease-aware launcher publication dependencies remain outstanding.
