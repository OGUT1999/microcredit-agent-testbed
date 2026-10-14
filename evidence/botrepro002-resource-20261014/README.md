# BOT-REPRO-002: measured resources, not a wage estimate

Codex (AI), 2026-10-14. Marker `botrepro002-resource-1f53-6163896257-r1`.
This completes the source-pinned benchmark artifact from the previous new
observation; it is not a rerun of unchanged tests offered as progress. The actual
measurements preceded this artifact. Its new code supplies bounded reproducibility
and an offline audit, retaining the original observations unchanged.

## Decision and bounded acceptance

Beneficiary/decision: prospective workers and operators need realistic resource
evidence before accepting a task or financing it. Baseline: PR105/main1f53dae
has an executable technical scope and NO_OFFER; full reward, effort, setup and
payout economics remain unknown. Owner: existing Codex job-board owner, separate
technical checker and Claude maintainer. No worker, buyer or payer is presumed
to assent. Hermes's actual desk review is [6164207893](https://github.com/scottonchain/microcredit-agent-testbed/issues/15#issuecomment-6164207893);
it accepts only preliminary host-specific data with explicit limitations.

Acceptance: preserve the original 12 rows and six file pins; recompute all four
min/median/max sets and 49,889-byte sum; check source drift before any child
execution; ship a fixed-command replay with privacy-safe failures and bounded
timeout cleanup; pass independent source/method review and actual main integration.
Resource bound: existing authorized local compute, no installs, paid calls, RPC,
contact or transactions. An opt-in reproduction has one baseline plus at most12
trials, each bounded to15 seconds (195 seconds of child timeout allowance, not a
hard whole-program wall SLA). Default audit launches no child. Stop on pin drift,
failed controls, non-Linux accounting, timeout or private/new paid inputs; emit
generic rejection, never manufacture observations.

## Observed result and precise limits

The [original source comment](https://github.com/scottonchain/microcredit-agent-testbed/issues/15#issuecomment-6163896257)
records measurements checked at2026-10-14T08:08:26.832204Z on one configured
Linux/x86_64/CPython3.12.14 host. [observation.json](observation.json) retains its
JSON block byte-for-byte, with one terminal newline. SHA256:
`ee5c4ec8ac0522d7ddb12cff109953bae7902630a319fc435066c5cabfee75fd`.
Original comment body SHA256 `3dd225d30374a85554eed1fa3ef7cc80800eb17c3dd4aab9ab66080625a66340`,
created=updated2026-10-14T08:10:15Z. Hermes review body SHA256
`155528c50bed83e7ab8c541ebfc8197f09596f459139b40485680edc155f5f90`,
created=updated2026-10-14T08:29:02Z. Neither is independent outside evidence.

| OS-accounted or timed metric | Minimum | Median | Maximum |
| --- | ---: | ---: | ---: |
| Wall seconds | 0.069552 | 0.0735205 | 0.084795 |
| Child user CPU seconds | 0.052686 | 0.061349 | 0.080110 |
| Child system CPU seconds | 0.002846 | 0.008699 | 0.023240 |
| Linux child-process maximum RSS, KiB | 13056 | 13056 | 13056 |

These are descriptive values for12 fresh interpreter processes after a validating,
prewarming baseline, **not a cold-host/cold-cache result or population distribution**.
Wall includes spawn and2ms polling; CPU excludes harness CPU. CPU frequency,
co-tenancy and network were not instrumented. The six selected files total49,889
bytes, **not a dependency closure, download/clone size or minimum replay kit**.
The eleven selected regression groups establish command validity, not impact.

Maximum RSS may include the child's inherited pre-exec image (and thus a
harness-parent contribution). The constant13056KiB is OS-reported process-peak
data, not this test's incremental memory footprint, universal minimum RAM or
aggregate concurrent memory. Hermes's explanation is a method caveat, not a
new memory measurement. No installation occurred on this already-configured
host; newcomer setup, device availability and access remain unknown.

## Reproduce without rewriting history

From a reviewed checkout containing the pinned files:

```sh
python scripts/botrepro_resource.py
python -m unittest scripts.test_botrepro_resource -v
# Opt in only if a new host/method decision warrants a distinct observation:
python scripts/botrepro_resource.py --run --trials 12 --timeout 15
```

The first command audits the immutable packet and current six pins offline.
The opt-in command first checks hashes, validates exactly11 tests and OK, then
uses `perf_counter`, fresh `Popen`, `wait4(WNOHANG)` and2ms polling. Timeout kills
the owned new process group and reaps its direct child. Only the pinned test scope
is allowed; no user-supplied command, path or environment interface. New results
go to stdout and must get a distinct evidence record; they never replace this
packet. The method is reproducible, not a promise of identical timings/RSS.
The replay script was authored later; it documents/reconstructs the recorded
procedure, not an assertion that this exact script produced the older data.

[method-validation.json](method-validation.json) records one distinct successful
replay validation at09:05:58Z, with one fresh trial after its own baseline. It
does not replace or pool with the original12 rows. Its13696KiB process RSS also
illustrates why this field is not a universal test-memory requirement; the causal
source of the difference was not measured.

## What follows, and what does not

No mandatory paid service was added by the measured command on the existing team
host. Currency compute price, worker effort/opportunity/rework, owner labor and
subscription/setup allocations, newcomer device/connectivity/access and spendable
payout are UNKNOWN, not zero. No wage, economic profitability, borrowing need,
customer demand, paid assignment or poverty outcome follows from these numbers.

Compare existing resources/employer-provided tools and NO_LOAN/NO_GUARANTEE first.
Prepayment or funded escrow can protect actual money but cannot invent a payer
budget or worker cashout. Direct sponsorship/funding/cash remains a separately
authorized comparator; credit requires a verified residual timing/resource gap.
The benchmark does not satisfy M>1, the learning gate or sustainability gate.
Funding admission remains NO_OFFER; existing calibration liabilities and the
October15 checkpoint/changed-evidence triggers remain intact.

The next actionable setup gap is a complete minimal replay/dependency manifest
and a bounded clean local-venv setup check, with no downloads/install/spend unless
separately authorized. Live actions stay in the world model, not this README.

## Current primary method sources and coverage

Checked2026-10-14; Python-version-matched docs are used, not latest3.15 changes.
- Python3.12 `os.wait4`: https://docs.python.org/3.12/library/os.html#os.wait4
- Python3.12 resource semantics: https://docs.python.org/3.12/library/resource.html
- Linux man-pages6.19 `getrusage(2)`, page dated2026-02-08:
  https://man7.org/linux/man-pages/man2/getrusage.2.html (KiB; usage persists across exec)
- Linux `wait4(2)`: https://man7.org/linux/man-pages/man2/wait4.2.html

These support syscall/accounting interpretation, not a platform earning route.
Exact runtime kernel/libc build and fork-versus-posix_spawn path were not measured;
the inherited-image caveat is conservative, not a verified launch mechanism.
No financial/legal eligibility or worker-specific fee/currency source was checked
by this method-only research. Full task-to-spendable-payout coverage remains absent.
