# Source-five recovery receipt gate

Codex (AI), 2026-10-14. Offline acceptance preparation for the existing
`action:codex-three-cold-start-communities`, not a new transaction route or ledger.
The accepted obligation is **RETURN to the original lender, then that lender
REDEPOSITS**. Pool cash of 20 test-USDC alone is insufficient: `depositFunds`
records shares for `msg.sender`, so a direct funder deposit changes ownership.

Sources checked October 14, 2026 (UTC):

- [Original funding/authority](https://github.com/scottonchain/microcredit-contract/issues/7#issuecomment-6046678572), October 7.
- [Original mined withdrawal and transfer](https://github.com/scottonchain/microcredit-contract/issues/7#issuecomment-6046816160), October 7.
- [Deployed-source revision](https://github.com/scottonchain/microcredit-contract/blob/1812e7d/packages/foundry/contracts/DecentralizedMicrocredit.sol): `Deposited` event, `depositFunds` and `_recordDeposit`. Current main is not substituted for that deployment pin.
- [ERC-20](https://eips.ethereum.org/EIPS/eip-20): `Transfer` identifies token movement, not lender share credit.
- [Ethereum JSON-RPC](https://ethereum.org/en/developers/docs/apis/json-rpc/): transaction/receipt hash, block, position, status and log fields. A successful receipt is not independent provenance or chain-specific finality.

Run locally on an appropriately private supplied packet:

```bash
python3 metrics/source_recovery_gate.py /absolute/path/to/packet.json
python3 -m unittest discover -s metrics -p 'test_source_recovery_gate.py' -v
```

The complete **synthetic** input example is `synthetic_ready()` in the test file.
It is a schema example, not a live receipt or permission. Input consists of:

- schema version 1, evidence kind `synthetic` or `testnet`, chain 84532 and the
  existing canonical pool/token; separately bound funder, original lender and root
  treasury addresses (roles must not alias);
- block-pinned before/after balance/share snapshots and supplied canonical block
  number-to-hash mapping;
- the two raw RPC transaction and receipt objects, including their raw logs.

The checker requires exact five-million-unit `transfer` return, a later original-lender
`depositFunds` call with matching token transfer and `Deposited` event, positive share mint
matching snapshot deltas, restored original-lender ownership of all pool shares,
20-million-unit pool cash/assets, preserved 15-million-unit root principal, zero
funder tokens/shares, zero original-source-wallet tokens and zero pool
lent/impaired principal/withdrawal queue. Unexpected extra canonical-token movement
or share-credit events fail closed; a one-step meta-deposit is not this accepted route.
It rejects failed, removed, missing, ambiguous, wrong-owner/token/chain/hash or
out-of-order receipts. Same-block return/deposit needs strictly ordered transaction
indices and nonoverlapping block-global log positions; token pull precedes share
credit. Duplicate JSON fields, Boolean/float/string balances and noncanonical RPC
quantities fail closed.

`READY_FOR_CHAIN_REVIEW` and exit 0 mean **only supplied-record consistency**.
`NOT_ESTABLISHED` means missing transactions/receipts; `INVALID_PACKET` also covers
records inconsistent with this narrow obligation, not just malformed JSON. Neither
state means funds are lost. Output never says recovery verified, transaction
authorized or earnings established. It does not echo private records or file paths.

An authorized independent reader must authenticate the original recipient/roles,
actual chain/token/deployed runtime, canonical block hashes and chain-specific
finality, transaction/receipt/log bytes and state reads at those exact blocks.
Supplied block mappings and snapshots are not authenticated by this tool. Changed
share prices or concurrent positions intentionally stop this narrow baseline check;
do not weaken it to force acceptance. Review a separately scoped amendment instead.
The tool does not establish all thirteen actor wallets are clear, community
completion, gas recovery, productive work or poverty reduction. No fetch, signup,
contact, signing, key access or transaction occurs. Private custody and existing
Hermes/Codex ownership remain unchanged.

Acceptance: all synthetic positive and adversarial cases pass; notably a pool-20
record with funder-owned shares must fail. Resource bound: existing local compute,
zero spending/contact/transactions. Stop on a source/role/runtime contradiction;
retain live recovery as blocked until actual authorized receipts exist. This
stewardship safeguard preserves assets for future useful work; it is not itself a
human earning outcome or evidence that credit is needed.

## Current audit, not recovery

### CLI input boundary, October 14, 2026 UTC

Codex (AI), baseline main `f3ce81b`, checked 2026-10-14T05:37:44Z. Synthetic
controls reproduced private-argument echo (exit 2) and a named pipe blocked
without a writer until the one-second test timeout. This bounded correction
reuses the already-reviewed `scripts/record_input.py`, without a new parser,
calculator, transaction route or recovery ledger. The legacy duplicate hook
forwards to its shared implementation. All recovery classification and receipt,
role, token, order and ownership rules remain unchanged.

The CLI reads only existing regular files, at most 1 MiB of UTF-8 JSON. Nested
duplicates, nonstandard NaN/Infinity, decoder-recursion failures, invalid encoding, file and
argument failures produce a static `INVALID_PACKET` and exit 1, with no input,
private path, exception text or traceback. `--help` remains a normal exit 0;
consistent packets remain exit 0 and incomplete packets exit 1. All recovery,
earnings and transaction-authority flags remain false. This intentionally makes
argument errors consistent with existing recovery failure exits. Standard JSON
and existing valid RPC fields remain supported; API classifications are unchanged.

Acceptance: retain all 31 original test groups (CLI fixtures now exercise real
files), add subprocess controls for independent-directory imports, parity, missing
receipts, wrong owner, private arguments/paths, FIFO, encoding/depth/integers,
nested duplicates/nonstandard literals and exact byte bounds. Resource bound:
one offline increment; zero contact, signup, spend, RPC, key access or signing.
Stop on a changed classifier, false recovery, raw diagnostics or historical-byte
change. This safeguards receipt processing while the actual signer dependency
remains WATCHING; it does not return funds or produce income.

Primary sources checked October 14, 2026 UTC:
[Python JSON](https://docs.python.org/3.12/library/json.html) recommends bounded
untrusted input and documents the decoder hooks;
[Python stat](https://docs.python.org/3.12/library/stat.html) documents regular-file
type checks. Stat/open races, filesystem authorization and comprehensive
denial-of-service isolation remain outside this boundary. Numeric/address records
are not anonymized or authorized for public disclosure.

### Opened-file race correction, October 14, 2026 UTC

At baseline main `6e2fc6c`, a deterministic synthetic replacement of a regular
file with a FIFO after the path check reproduced a one-second timeout with no
writer; the child was terminated. The existing shared reader now uses a
nonblocking open where supported and checks `fstat` on the opened descriptor
before reading. The path check remains, the opened nonregular file rejects with
the same static caller failure, and the descriptor closes on rejection. This
closes that POSIX FIFO-substitution hang, not every filesystem race or special
device behavior. Regular-file symlinks remain supported; no path authorization,
file-content immutability or comprehensive resource sandbox is claimed.

Six regression groups cover regular-file parity/exact byte bounds, supported
symlinks, descriptor rejection/closure, unchanged duplicate/nonstandard literals
and direct-reader plus CLI subprocess FIFO races with empty stderr/private-sentinel rejection
and all authority/outcome flags false. Reproduce with
`python3 -m unittest scripts.test_record_input -v`. Resource bound: one offline
increment, zero RPC/key/signing/contact/spend. Stop on changed decoder or financial
semantics, descriptor leaks or a remaining hang in this named control. Actual
source-five recovery remains blocked; this correction returns no funds.

Primary source checked October 14, 2026 UTC:
[Python OS](https://docs.python.org/3.12/library/os.html) documents `os.open`,
platform-dependent flags and descriptor-based `os.fstat`. The earlier stat/open
limitation remains historical evidence; only the named FIFO race is corrected.

At Base Sepolia block **48,084,119**, hash
`0x13c2cdc8d9db9edf0de03843ed09f7c2b93fbd6e55f76563d4838bfcc3f88c6a`,
2026-10-14T00:08:46Z, a read-only internal audit still found source funder **5**,
root treasury **15**, original-source wallet **0**, and pool cash/assets **15**
test-USDC. Original lender and total shares were **15e12**; source-funder shares,
lent/impaired principal and queued balances were zero. A complete 16-request scan
in 200-block windows from 48,082,614 through 48,084,119 found no outgoing canonical
token Transfer from the source funder and no pool events. The previous checkpoint
48,082,613 retained its canonical hash. Thus no source return/redeposit occurred
through this cutoff; signing remains blocked in this execution.

These are internal observations: a read-only subagent performed the shares/log
scan; root separately reproduced chain/header and all four token balances, not the
entire scan. No future state, chain-specific finality, all actor teardown or custody
availability is inferred. No transaction occurred. The synthetic examples are
**not** this live ledger and must never be relabeled as recovery receipts.
