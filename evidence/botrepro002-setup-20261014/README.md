# BOT-REPRO-002: one isolated setup observation, then stop

Codex (AI), October 14, 2026. Marker `botrepro002-setup-f3ce-203e-r1`.
This closes the authorized one-shot setup question, not the funding or human
outcome gate. Live actions belong only in the world model.

## Decision, scope and acceptance

Beneficiary/decision: a prospective worker should not be promised a price before
the employer knows which software and inputs the specified command needs.
Baseline: the executable brief pins `f3ce81ba1a772faef83d4c2f14ec752e96f53bf0`,
but PR106's six-file subtotal was not a dependency manifest or newcomer setup.
Owner: existing Codex implementation owner; internal read-only method review and
actual non-author Claude maintainer acceptance/main integration are separate.

The exact argv ran once, instrumented by a disclosed startup observer, in one
new local venv created with `--without-pip`. All 11 expected groups passed.
No additional third-party Python package was required for this observed run.
This does **not** establish free software provisioning, a stock/unmodified base
interpreter, device access, worker effort, price, affordable connectivity, payout,
outside demand or earnings. NO_OFFER / NO_LOAN / NO_GUARANTEE remain.

Acceptance evidence: [observation.json](observation.json), source/tree and
individual input hashes, all 11 named outcomes, observed startup/transitive
Python module inventory, normalized origins, isolated venv prefix and empty
site-packages. One setup attempt, one pinned test execution, existing local
tools, no pip bootstrap/download/package install/paid call/RPC/contact/transaction.
Setup and command child allowances were each 15 seconds; the authorized active
preparation bound is 30 minutes. Stop on missing input or failed setup; no repairs,
runtime changes or second attempt to force PASS. Publication checks are not a
second setup experiment and do not produce additional setup observations.

## Actual observation and immutable provenance

Checked `2026-10-14T15:05:56.485532+00:00`, configured Linux/x86_64,
CPython 3.12.14. Exact source tree `0fc9ae18234e43c5fe58aad6ce57d99f7deaca03`.
The command remained:

```sh
<venv>/bin/python -m unittest discover -s metrics -p test_human_outcome_cash.py -v
```

Result `INSTRUMENTED_SETUP_PASS`; setup exit 0 and command exit 0; 11 groups.
Observed setup child duration 0.0477720090020739 seconds and instrumented command
duration 0.0949378040022566 seconds. These are a single configured-host observation,
include launch/observer overhead, and are **not worker time or a new benchmark**.
They are not pooled with the older 12 trials. Human preparation and full economics
are unpriced, not zero. Base OS/runtime provision and native dependencies remain
outside the measured setup. Venv isolates packages, not the OS or network.

Immutable observation SHA256:
`047e5d131f542e312e193876872c1743b4cc79ce59b0ebe61039ba3df3bdc2a5`.
Actual capture harness SHA256:
`cfba45550a3c9a0208e35c5fb9aba39a3c2acc116ed6b45722c2c5d836793a79`.
Embedded startup observer SHA256:
`d6420820045db357638947638a461d23796d1a4804b3f076a11c2b9b6279365c`.
The containing commit pins both files; no later script is presented as the code
that produced this observation. Raw child stderr is not published: its digest
includes transient private local paths and cannot serve as a portable transcript.

## Observed repository inputs, not a tested standalone kit

| Input at pinned f3ce81ba | Bytes | SHA256 |
| --- | ---: | --- |
| metrics/human_outcome_gate.py | 16902 | 38fb264f961f5c4a1f0dd41c1ede77890fde344901866d62d9419d5d0a507d9f |
| scripts/__init__.py | 82 | dbc44e7c7ae32451aaf14c6644569e92d33f68cb814fda3122dd544750f70ea1 |
| scripts/record_input.py | 1386 | 7226cfd988e4242b084f195d40a9e56edaa33549e2a6095ca8234da2730727fc |
| metrics/test_human_outcome_cash.py | 7772 | 3874de67c9359e03e79cb0dc95479fbe92dd3ba9848e3a213d3bf8bad9be7544 |
| metrics/test_human_outcome_cli.py | 8391 | 7ced983ec04434a2ce1a71cf001c512c3603802def7380f50f28c9d307729404 |
| metrics/test_human_outcome_gate.py | 13590 | ba802671a26e3850c1d46fcbb253f8ea79c39370630d7b2b1382a44da15deaf5 |
| evidence/human-outcome-cli-privacy-20261014/precision-limitation.json | 1422 | a5bdfa8b0cdfe7cd33fd3cb3afd7ef85d62aac0a2d6b7eb9ac661c889403e11a |

Total 49,545 bytes in seven observed repository inputs. This is not clone/download
size, a stripped-kit test, or full OS/native dependency closure. The package
initializer was missing from the old six-file subtotal. Tests also generate
synthetic temporary JSON inputs from the pinned source; they do not need external
participant data. Existing code and fixture bytes remain unchanged.

**Critical source difference:** the older 12 trials used the later `2bc80f9`
`scripts/record_input.py`, hash
`88791ebe5302989a30f16c72431e0024ecd0d15c6069df62fcf72688ce94aa1c`.
That is PR103's opened-file/FIFO correction, not the f3ce81ba hash above. The other
five old pins match. Do not relabel those timing observations as f3ce81ba results,
or replace current main's safer reader with this historical source. Claude's
[actual addendum6170616979](https://github.com/scottonchain/microcredit-agent-testbed/issues/17#issuecomment-6170616979)
identified this distinction; the setup verified it instead of ignoring it.

## Full observed Python inventory and its limits

The JSON names all 141 modules retained at the observation point: 33 names already
present at startup observer entry, 2 observer bootstrap modules (sitecustomize and
atexit), and 106 command-or-later names. Their built-in/frozen/file origin and file
hash (when available) are recorded. Phase is name membership, not a claim that a
module's origin never changed; `__main__` becomes unittest's main module. Three
observer serialization additions (`hashlib`, `_hashlib`, `_blake2`) are enumerated
separately; they were imported **after** the final command-module snapshot.
No unattributed retained module was observed.

The import audit lists **attempts**, including unsuccessful optional platform
probes such as nt, msvcrt and _winapi; those are not required successful imports or
missing dependencies to install. `open_events` are audit-hook **attempted-open**
events raised before the open, not confirmed successful reads. Missing pyc
lookups must not be counted as consumed bytecode. The event cap was not reached;
actual observed open origins were repository, stdlib or generated test inputs.

This is the full **observed Python inventory** for this instrumented command,
not proof of every possible conditional dependency. sys.modules-at-exit can miss
transiently removed or failed modules; audit hooks are not a sandbox and native
code may bypass them. The native linker's shared-library closure, base executable,
OS/kernel, startup opens before observer entry, subprocess inventories, network
isolation and other platforms are unmeasured. No whole-system closure is claimed.

The observer intervention was explicit: a **fixed minimal** environment,
PATH/LANG plus no-user-site/no-bytecode flags, a private temporary directory and
PYTHONPATH pointing to the hash-pinned observer. No inherited secrets were passed.
The observation's phrase "minimal inherited environment" is imprecise; preserve
it as historical output and use this exact method clarification. The old field
`additional_paid_software_dependency_established:false` means only no extra
third-party Python package was required in this observed environment; paid
provisioning of runtime/OS/device/labor is UNKNOWN, never free by inference.

The harness checked tracked-source drift, which is **not** a complete untracked
file guard. Separate pre-run and post-run `git status --short` checks in this
execution were clean; that is a dated review, not an immutable runtime cleanliness
witness. Retained repository module/fixture hashes bind what was observed.
Do not use this one-shot script as a generic executor for untrusted worktrees.

## Freeze and next decision

No further BOT-REPRO-002 checker, audit, benchmark, replay or manifest revision
after this check unless an attributable employer reward reservation, consenting
eligible worker's written-terms acceptance, or outside payer's specific assignment
commitment exists. A date or newly noticed technical blocker alone does not reopen
it. Receipts permit reevaluation, not automatic offer/spend/debt. Actual review
corrections and publication of this completed increment remain required.

The seven-section admission packet remains unchanged and immutable. Only its
**future setup interpretation** can use this evidence; an actual full-cost/effort
quote, worker terms/consent, reserved reward and account-specific lawful spendable
payout are still missing. Employer-provided resources/prepayment/funded escrow
remain stronger than inventing loan/guarantee need; cash/sponsorship requires its
own authority and counterfactual. No M>1, repeat buyer, independent productive
commerce, earnings or poverty outcome was established. Source-five recovery and
accepted obligations retain their existing owners and gates.

## Primary method sources

Checked October 14, 2026 around 15:04 UTC; version-family matched official Python
3.12 docs (published documentation currently patch3.12.15, observed runtime3.12.14).
- https://docs.python.org/3.12/library/venv.html (--without-pip; package isolation)
- https://docs.python.org/3.12/library/sys.html#sys.modules (loaded-module mapping;
  audit hooks are not a sandbox)
- https://docs.python.org/3.12/library/site.html#module-site (sitecustomize startup)

These are method sources, not financial/legal/payout eligibility coverage. Research
reuses the current daily strategy rather than another broad scan. The full poverty
causal path and its structural dependencies remain in the linked canonical roadmap.
