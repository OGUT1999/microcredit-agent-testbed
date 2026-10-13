# Synthetic offline integration preparation

Codex (AI), continuation of draft PR90 at prior head
`4d9e1268acb8c2e1ccca6c972a40809ff2b69e42`. Main reviewed at
`3b1ed48cf2fa0537db2afbd46365c51ed079cb9b`, model 0.1.117; issue79,
PR80, merged PR82 and board15 ownership were reread. Fieldwork PR89,
payout-quote work and DNS/vision receipt owners are unchanged.

This test serves the decision whether the preparation's Python market and
receipt-import plumbing can compose under bounded synthetic inputs. The cheapest
evidence is deterministic local fixtures and adversarial rejection tests. This
makes no case that credit or guarantees beat client prepayment, sponsorship,
existing payment protection or NO_LOAN, and changes no human-benefit baseline.
Stop this path if isolation, consent binding or accounting rejection fails.

## Run

From the repository root, with existing Python (standard library only):

```bash
python experiments/guarantee-trust-real-agents-seven-days/offline_integration.py
python -m unittest discover -s experiments/guarantee-trust-real-agents-seven-days -p 'test_*.py'
python tools/check.py
```

No new dependencies are added. The existing isolated ethers 6.15.0 package and
lockfile are untouched. This entrypoint does not need Node or ethers, does not
invoke the launcher, executor or JavaScript verifier, and does not install or
run lifecycle scripts. Historical recovery/runtime results remain unchanged;
the inaccessible old uncommitted work remains unrecovered.

The CLI removes its environment before creating the scenario. It creates a
new temporary synthetic run and deletes it afterward; it accepts no run-directory,
RPC, key, URL, model or publication arguments. The application-level provider
has only a finite in-memory fixture table and an allowlisted method; missing data
raises instead of falling back to RPC. Signing, broadcasting, network/model and
publication transports raise on every call. A process-local Python audit guard
rejects sockets and subprocess execution, including bypass attempts inside an
injected verifier. No OS network or persistent security configuration changes.
This guard protects the reviewed Python path; it is not a sandbox for arbitrary
native code or untrusted plugins.

`ReceiptBridge` now accepts an explicitly injected verifier only for state labeled
`synthetic-offline/1`. Such state cannot fall back to the production subprocess
verifier, and injected results must carry the same synthetic label. Ordinary
production state rejects injected transport. `Market.import_receipt` forwards
this optional keyword, so integration uses the actual registration, defense-in-depth
decoded checks, replay protection, accounting and file persistence code.

## Covered path and honest limits

- Synthetic bootstrap stub, then 400,000 reserve funding (the actual day-one
  market limit), a 200,000 wage and an 80,000 guarantee (20% of seed).
- Actual market job posting, application, client hire, worker acceptance,
  guarantee proposal, delivery, acceptance and payment proposal.
- Exact typed-action transcript records labeled SYNTHETIC. Client ID is SHA256
  of the actual market client ID; terms hash derives from the actual hired job.
  Opening consent records include fixed nonce/deadline fixture fields before
  acceptance, but no signature or EIP-712 domain verification occurs.
- Four injected decoded receipts: fund reserve, open, pay 190,000 net, mark-paid
  200,000 gross. Final synthetic market status is `paid`. The 10,000 difference
  is **not** remitted pool contributions; no custody settlement is claimed.
- Seven day barriers consume 700 explicitly labeled static empty-command pass
  packets through `submit`/`advance`. These are canned test data, not model
  invocations, fresh agent decisions, real participation or a seven-day demo.
- Negative tests cover altered/rehashed consent, changed nonce, wrong terms or
  client, initial budget excess, replay, ambiguous duplicate transfers, missing
  fixtures, stale pins, wrong chain, missing synthetic labels, missing transport,
  live-state injection and publication/network/signing/broadcast/process attempts.
  Rejections assert both state and persisted files are unchanged. Ambiguous
  transfer rejection permits a subsequent corrected fixture import.

The verifier/provider return fabricated decoded data and a fabricated bootstrap
assertion. Public root/token addresses are schema values only; no keys are used.
The real JavaScript receipt verifier, RPC/ABI/log decoding, token semantics,
cryptographic consent, contract enforcement and EVM are **not exercised**.
Attestation, claim, cancel, auxiliary wallet actions, interruptions across process
restarts, reserve solvency and complete custody unwind are not integrated here.
Existing pure predicate tests are not substitutes for those paths. The transcript
hash and synthetic summary are deterministic; receipts never assert live readiness.

## Inherited open gates, not resolved or introduced here

Static review before this continuation found the PR90 executor, launcher, market
and verifier blobs equal to PR80. The following remain inherited gaps:

1. `comment-launcher.mjs` lines 61–63 fork public RPC without a pinned block;
   line 41 inherits the environment; lines 72–80 can push main in `finally`.
   It remains unsafe to run and needs a reviewed lease-aware publication design.
2. `executor.mjs` lines 83–93 require a real root key even for rehearsal.
   This entrypoint avoids that executor; it does not repair key custody.
3. Market `--dry-run` isolates files only; the production bridge still invokes
   `receipt_verifier.mjs`, whose public RPC fallback remains. The new synthetic
   entrypoint has separate injected transports and fails closed.
4. The older day-one fixture funds 500,000 against the market's 400,000 cap,
   and its client/terms hashes differ. This new fixture is consistent; the old
   fixture is preserved and not declared repaired.
5. Executor consent at lines 188–203 precedes later-resolved nonce, deadline,
   domain and message, contrary to README line 60. The synthetic test's exact
   fields do not validate or fix production cryptographic authorization.
6. `settlementComplete` at executor lines 279–282 covers guarantees, not retained
   funds or unremitted custody. Full settlement remains unproven.

Next gates: independent review of this exact delta; production signing/consent
and full custody review; separately authorized pinned-provider/EVM rehearsal
covering every auxiliary action and failure path; actual fresh-context model
harness; safe launcher publication design. Workflows remain disabled. Maintainers
retain merge authority. No deployment, signature, transaction, paid model,
prospect contact, live story, benefit claim or new schedule is part of this pass.
