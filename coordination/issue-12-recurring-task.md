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


## Lossless live-state encoding compaction

After this protocol amendment receives non-author review and is incorporated into
main, an owned-lease writer may compact only JSON whitespace in comment 5999201336.
This is not archival and permits no removal, summarization, key renaming, cursor
advance, status change or relocation of data. In particular, retain
`required_safety_ctr41` and `required_safety_tb181` at their existing paths.

Re-read the live body and updated timestamp under the existing lease. Parse the
single JSON fence with duplicate-key rejection; reject non-standard JSON values.
Serialize the same decoded object with compact separators and unchanged key order.
Require complete decoded-object equality before and after, and preserve every byte
outside the JSON payload. Do not combine this operation with semantic updates.
Run the public-content check, assert exact lease ownership, and require an
unchanged-body/timestamp reread before PATCH. Re-read the saved body and verify
exact bytes and decoded equality. On mismatch, stop protected work and reconcile;
never overwrite a concurrent writer. Record before/after sizes and the outcome in
the next ordinary receipt, without creating a second ledger.

Later writers must preserve compact encoding once adopted, applying normal lease,
privacy and unchanged-body checks to their actual state updates. Existing immutable
snapshots remain untouched. The archival section still governs removal of historical
entries; this encoding rule does not authorize pruning operator-directed actions.


## Archive pointer index

The `continuation_receipt_archives` list grows by one reference per pruning step and
now holds about a sixth of the comment (its list serializes to 10,108 of 65,008
characters at 03:03:59Z). This amendment lets its older entries
live in an immutable repository file that a single pointer names. It is not a
migration: it moves no live data until a separate, reviewed step below, and it adds
no lock, controller, cursor or permission. The tool is
`coordination/issue12_archive_index.py`; its tests run with the coordination suite.

Index files are `coordination/archives/index/issue-12-5999201336-v###.json`
(format `issue12-archive-pointer-index-v1`, serialized with `indent=2`,
`ensure_ascii=False` and one trailing newline). Each holds the exact entries, in live
order and with every field, plus a count and the SHA-256 of their compact
serialization. A merged index file is never edited or deleted. A later version is a
new file that holds every entry of the one before it and names that one in `previous`
(commit, path, SHA-256); only the version the live pointer names is current.

The pointer is the first element of the list and has exactly these fields:
`index_commit` (the merge commit that added the file), `index_path`, `index_sha256`,
`entries` (the count) and `last_snapshot_sha256`. The lookup rule is unambiguous: the
full archive list is the pointed-to index's entries followed by the remaining inline
elements, in order. A pointer anywhere else, a second pointer, or a pointer that
disagrees with its file in any field is an error. Readers and writers use
`resolve --body-file BODY --repo CHECKOUT` to rebuild the list; `check` reports the
state and, with `--ancestor-of origin/main`, requires the pinned commit to be on main.
They fail closed: a missing file, a changed byte, a non-canonical serialization or an
unreachable commit stops the work and the comment is read as unresolved, never guessed.

Pruning is unchanged. After the pointer exists, a pruning step appends its own
reference inline after the pointer exactly as before, under the snapshot, review and
unchanged-body rules above. Nothing about snapshots, the retained receipts, the
`required_safety_ctr41` and `required_safety_tb181` fields, operator-directed
actions, missed triggers or completed-trigger identifiers changes. Only the archive
references move, and this amendment does not authorize relocating anything else.

The first replacement may happen only after all of these hold:

1. The index file and this amendment are on main through non-author exact-head review,
   and the pointer's `index_commit` is that merge commit.
2. An owned-lease writer rereads the comment body and `updated_at`, then runs
   `migrate`. The leading `entries` elements of the live list must equal the index
   entries exactly; newer inline elements stay in place. A difference inside the
   indexed run means stop, rebuild as a new reviewed version and never overwrite.
3. The tool's dry run proves that `resolve` of the new body returns the old body byte
   for byte, and the new body is checked against the 65,536-character limit and the
   public-content check. `migrate` makes this check before it writes `--out`, so a
   refused command leaves no candidate file.
4. PATCH only after an unchanged-body and timestamp reread, then reread the saved body
   and verify its bytes and that `resolve` of it equals the pre-replacement body.
   Record the before and after sizes and hashes in the next ordinary receipt; do not
   create a second ledger. On any mismatch stop protected work and reconcile.

When inline references accumulate again, a roll-up is the same procedure with
`build --version N+1 --previous-json ...`: build the next index from the full
resolved list with `previous` set to the live one, review it, merge it, then replace the pointer and the inline
references it covers with the new pointer. The equality test differs by case. The
first migration compares bytes: `resolve` of the new body must equal the old body,
which has no pointer. A roll-up compares expanded forms: the old body still holds
the previous pointer, so `resolve` of the new body must equal `resolve` of the old
body, and both must name the same full list. `migrate` prints that expanded hash
(`expanded_sha256`) for the receipt.
