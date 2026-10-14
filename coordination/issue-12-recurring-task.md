# Protected Git writes and continuation records

Read the [team operating guide](README.md) for current work selection, ownership,
communication and recurring responsibilities. This file owns the verified Git
lease and protected-cursor protocol; it is not a second backlog or scheduler.
The [October 6 setup and prior task snapshot](https://github.com/scottonchain/microcredit-agent-testbed/blob/d4f5b4f4a0783e696fb9a740692655e94afd7f0e/coordination/issue-12-recurring-task.md)
remains in history. Current original evidence and operator directions supersede
that snapshot's old priorities, email-first wording and README format.

## Capability requirements

Capability must be established in the actual execution environment. A prior clone,
interactive push or scheduled prompt does not prove a future worker can write,
serialize work or protect its identity. The previous connector commit path did
not expose explicit author/committer parameters, leaked a personal email, and did
not establish atomic conditional ref updates. **Connector-only protected work
remains read-only unless the operator-authorized connector exception below is satisfied.** Do not create a probe commit, change privacy settings or use
an unverified expected-SHA argument as a substitute for the protocol below.

Require actual authenticated Git with explicit noreply author and committer plus
server-atomic exact leases. Scheduled serialization is not assumed. The old
implementation writer stays disabled; this runbook neither revives it nor changes
any schedule. On a credential failure, stop protected writes and retain an owned
lock until its safe release is possible. Finish useful read-only work and provide
an exact patch/handoff when writing is unavailable; a request to Claude is not a
publication receipt. Append-only messages must also follow their current rules.


## Operator-authorized GitHub connector path — 2026-10-12

The operator confirms that GitHub account email privacy and push-email blocking are enabled and that their configured GitHub email is a privacy address. The operator explicitly authorizes direct GitHub connector edits and merges so that routine maintenance need not depend on Claude. This changes the blanket connector-write prohibition **conditionally**, not the project privacy, review, or concurrency goals.

- Before a connector write, verify that the actual commit author AND committer email to be recorded are privacy-safe. Account profile email alone does not establish the commit identity. If either address is exposed, unknown, or unverifiable, do not write through that connector; use the established noreply Git-shell route.
- For a focused ordinary-file update use the current file blob SHA, re-read immediately before modification, and verify the resulting commit identity and content afterward. Never overwrite concurrent edits. For PR merges compare the current head and diff, review required checks and policy, pass the exact expected head SHA, and verify the merged result. Do not merge an incomplete artifact merely to clear a queue.
- The Git-shell cooperative lock is still required for the protected state/cursors and writers governed by its protocol. A connector expected-head parameter is **not** a demonstrated replacement for the lock's server-atomic lease. Until a connector transport is independently verified for those invariants, protected record mutations stay on the verified Git-shell path.
- Ordinary issue/PR comments and reviews may use their existing connector paths, with author attribution and idempotent stable markers. Do not duplicate handoffs or weaken permissions for spending, deployment, outreach, privacy, or protected records.
- The operator's authorization removes a process bottleneck; it does not waive acceptance tests, editorial rules, independent technical review, archive-integrity checks, or required legal/financial approvals.

## Verified Git-shell protocol

`coordination/run_lock.py` operates only on
`refs/heads/coordination/issue-12-run-lock` (or a dedicated verification branch).
Never write lock state to `main`. It accepts the repaired `d78a70c` unlocked
bootstrap and records `git-explicit-lease-v2` on acquisition.

1. Read the exact remote head and `LOCK.json`. A missing, malformed, unknown or
   already-held lock stops protected work. Use fresh random public owner and
   execution tokens; keep their mapping to private scheduler records private.
2. Create an acquisition commit whose sole parent is that unlocked head, with
   explicit `Codex (AI)` noreply **author and committer**, verified before push.
3. Push with `--force-with-lease=<exact-ref>:<observed-oid>` and read back the exact
   candidate OID. Git's explicit lease requires that precise old OID at the
   server; sibling candidates cannot both advance the ref. All transitions are
   children of the observed head, so history never resets to an old unlocked OID.
   Do not substitute the connector's similarly named argument.
4. Preserve the acquisition OID and owner token. Refresh authoritative records
   after acquiring. Recheck exact ownership before every group of shared writes.
5. In `finally`, after all owned mutating work has stopped, release only if both
   owner and acquisition OID still match. Push a new unlocked child using the
   exact lease. A successful Git push acknowledgment completes the release:
   another run may acquire immediately afterward, so a later head is not a
   release failure. The returned release OID is a receipt, not a promise that
   the ref remains unlocked. Acquisition still requires exact-head readback.
   Never reset to the bootstrap, delete the production lock, or
   release another run's lock. On errors/uncertain outcomes stop protected work,
   read back for diagnosis, and do not repeat actions blindly.

This is a **cooperative mutex**, not access control against an arbitrary writer
with repository credentials. All Codex workers that mutate these records must use
this protocol; never run the older force-update connector protocol alongside it.
Other project agents retain their existing ownership/review processes.

There is no timeout takeover or automatic recovery command. Age, silence, a
missed heartbeat, or an old board comment cannot prove a run stopped. If a worker
crashes, retain the lock. A maintainer can recover only after authoritative
execution records prove the owning worker **and its delegated work** have ended;
record that evidence privately, preserve a public recovery receipt, and perform
an exact-head conditional transition. If execution liveness cannot be resolved,
continue read-only and report the dependency once. Never steal from a possibly
live run. A failed release is not permission to remove the lock.

Usage from the root of an isolated checkout (retain these values privately for
cleanup):

```python
import uuid
from coordination.run_lock import Lock
lock = Lock()
owner = 'codex-' + uuid.uuid4().hex
execution = 'run-' + uuid.uuid4().hex
acquired = lock.acquire(owner, execution)
try:
    lock.assert_owned(owner, acquired)
    # Refresh inputs, reconcile receipts, perform authorized work, save state.
finally:
    # First await/stop any mutating subprocesses; never release beneath live work.
    lock.release(owner, acquired)
```

CLI equivalents: `status`, `acquire --owner TOKEN --execution TOKEN`,
`assert-owned --owner TOKEN --acquired-head SHA`, and
`release --owner TOKEN --acquired-head SHA`. There is intentionally no `recover`
or implicit bootstrap command. Do not publish actual session IDs or private
scheduler identifiers as the tokens.

Run the focused suite from the repository root:

```bash
python3 -m unittest -v coordination.test_run_lock
```

Or from inside `coordination/`:

```bash
python3 -m unittest -v test_run_lock
```

Evidence: `validation-20261006.json` records a real remote race from independent
clones: one acquisition, competitor rejected, non-owner release rejected, held-lock
takeover refused, owner release succeeds, stale candidate rejected after release,
and noreply author/committer verified. The dedicated verification branch was then
removed with an exact-head lease. `test_run_lock.py` additionally tests an old lock
and malformed/missing states against real local Git remotes. This demonstrates
this Git transport, **not a scheduled execution or connector CAS**.

Reference: [Git push explicit-lease documentation](https://git-scm.com/docs/git-push).

## Protected input and outcome records

Before shared writes acquire the lease and reread canonical comments
**5999201336** (testbed #12) and **5999791943** (theory #1), current board inputs,
relevant PR heads, reviews and original evidence. Read complete relevant pagination
and edits. Hermes may work through other channels; an old board timestamp is not
proof that it is idle. Keep lock activity off main and do not hold it while waiting
for an agent, researching or running a long independent test.

Update the existing protected records only under the lease; do not replace them
with parallel cursor files/comments. Preserve other agents' content. Record input
IDs **and updated_at**, PR heads/review IDs, actual owner, dependency, next action
and completed stable markers, including the board cursor in the testbed record.
Use real source timestamps, never fabricated ones. Never advance past an unresolved
action. Ordinary append-only research handoffs do not silently advance protected
implementation cursors.

Use a deterministic marker derived from source ID and relevant revision; find it
in the destination before posting. After a crash or uncertain response, reconcile
actual remote outcomes before retrying. Save completed outcomes, stop/await all
owned mutations, then release only the exact owned acquisition. A missing or held
lock blocks protected writes; preserve it and do independent work. No repeated
unchanged blocker comments, stale takeover, replacement lock or quota workaround.

Internal reproduction is not independent outside review. Preserve calibration
terms, source pins, unfavorable findings, consent and financial/deployment bounds.
Use a branch and focused checks. Maintainer integration follows actual current
operator authority; cleanup permission does not grant public-chain execution.
Report a later scheduled worker as verified only after its own capability check,
new-input processing and outcome receipt, not from this manual setup/runbook.

## Bounded history archival

Comment 5999201336 remains the authoritative live state. When its size approaches
GitHub's comment limit, preserve an exact UTF-8 body snapshot with source URL,
source updated timestamp and SHA-256 in `coordination/archives/`. These immutable
historical snapshots are evidence, never another cursor, scheduler or live ledger.
Use the existing lease, explicit noreply identities, public-content checks and
maintainer review for publication. Do not prune the live comment merely because
an archive branch or PR exists.

After the archive is reviewed and incorporated into main, an owned-lease writer
may replace only matching entries from `previous_continuation_receipts` with a
`continuation_receipt_archives` reference naming the immutable commit/path, source
revision and body SHA-256. First verify the remote snapshot hash and complete JSON
round trip, reread current state, and compare every removed key/value against the
snapshot. Retain newer or changed entries. Keep completed-trigger IDs, latest
receipts, ownership, unresolved dependencies and all other live fields unchanged;
never advance an unresolved cursor. Check the resulting comment, PATCH only after
an unchanged-body reread, and verify the response. Archive lookup supplies the
removed historical entries; it does not supersede the live record. Do not delete
or rewrite a published snapshot. Missing review or hash mismatch stops pruning.

The initial snapshot `archives/issue-12-5999201336-20261014T210452Z.json`
retains the entire body as last updated at 21:04:52 UTC, including all historical
receipt values. This source change alone does not alter or prune the live record.
