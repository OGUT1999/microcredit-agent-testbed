# Existing ordinary-evidence source: offline prerequisite

Codex (AI), October 15, 2026. This bounded safeguard addresses the actual
integration bottleneck exposed by [PR125](https://github.com/scottonchain/microcredit-agent-testbed/pull/125).
That four-file source was integrated without creating a new commit identity.
It does **not** establish a general connector writer or protected-state route.

## Scope and decision

The beneficiary is the evidence reviewer and, indirectly, prospective workers:
the next source publication must not silently include protected planning state,
expose a personal commit identity, or replace a concurrent main revision. This
is stage-0 integrity work under the [conditional roadmap](POVERTY_ELIMINATION_ROADMAP.md),
not accepted paid work, a new buyer, human earnings or poverty reduction.

Baseline: prior integrations required manual inspection of commit topology,
identities and paths. A source-only request and passing CI did not prove those
conditions. `ordinary_evidence_preflight.py` now checks those local prerequisites
against actual Git objects. It creates no commit, updates no ref, performs no
fetch/push and never acquires, releases or substitutes for a lease.

This deliberately supports only one complete three-record packet
`evidence/<lowercase-slug>/{README.md,sources.json,validation.json}`, optionally
with `coordination/POVERTY_ELIMINATION_ROADMAP.md`. Every changed path must be
declared exactly once. It accepts only regular non-executable additions or
modifications, a sole parent equal to the exact base, and exact expected noreply
author **and** committer. Full lowercase 40-hex commit IDs are required; revision
expressions, shallow/partial/promisor stores, replace refs and grafts reject.
Effective repository/worktree configuration and included files are inspected;
checking only the common local config would miss a worktree promisor setting.
Inherited Git overrides/traces are discarded and lazy object fetching is disabled.

The tool intentionally rejects its **own code/test/documentation change** and
other ordinary-file updates outside this allowlist. Those need the normal
independently reviewed source path, not a widened packet scope. Do not weaken
this gate merely to clear a queue.

## Reproduce the actual source distinctions

From a complete trusted local checkout containing these existing objects:

```bash
python coordination/ordinary_evidence_preflight.py \
  --base 4dedd0c1de1631167c1746ba1dd4ccfbcf444b1e \
  --head 03da5f772b124d6b25535de5b43969118979d6a0 \
  --author-email hermes-agent-909@users.noreply.github.com \
  --committer-email hermes-agent-909@users.noreply.github.com \
  --path coordination/POVERTY_ELIMINATION_ROADMAP.md \
  --path evidence/x402-merktop-qualification-20261015/README.md \
  --path evidence/x402-merktop-qualification-20261015/sources.json \
  --path evidence/x402-merktop-qualification-20261015/validation.json
```

Expected: exit0, `LOCAL_METADATA_MATCH_ONLY`, `authorization:false`. Replacing
only `--head` with PR124's `b24ca7d9c357e9652f5a1b708d7c635c28cac614`
must reject `EXACT_PATH_SET_MISMATCH`: its extra model delta is protected.
Using current main `03da5f77...` as both base and head must reject
`SOLE_PARENT_MUST_EQUAL_BASE`, not reinterpret an old inspection as current.
The tests additionally model an unrelated concurrent successor.

Static failures omit supplied identities, repository paths, bad arguments and
Git stderr. Successful output includes object IDs, not commit-message text or
the raw path/identity inputs. Run only against a trusted local Git repository;
this is not a sandbox for hostile executables or configurations.

## Remaining gates are mandatory

`authorization:false` is intentional even on exit0. The tool does **not**:

- authenticate controllers, sources, reviewer assent, payment or impact;
- scan file contents for private data, prove the diff is useful, or approve an
  edit to immutable evidence; a historical packet modification still needs a
  separately identified reviewed correction and archive-integrity checks;
- establish current remote main, required policy/checks, legal authority or a
  maintainer decision; passing a local check is not permission to write;
- replace `scripts/check-public-content.sh`, required CI/non-author review,
  the established protected Git-shell lease, or independent default readback.

Immediately before any separately authorized ordinary ref update, refresh remote
base, source head/diff, policy, checks, review and ownership. Identity verification
applies to every new commit object; an existing safe commit is not proof that a
connector-created commit or merge would be safe. Use **non-forcing** server
fast-forward only; a sibling race must reject, never force or quietly rebase.
GitHub's [primary Git-reference documentation](https://docs.github.com/en/rest/git/refs#update-a-reference)
(checked October 15, 2026, 05:03 UTC; publication date not established) describes
this server fast-forward condition. A connector expected-SHA precheck is not a
demonstrated atomic lease. Protected files/state/cursors remain on the actual
[Git-shell protocol](issue-12-recurring-task.md#verified-git-shell-protocol).

## Acceptance, bound and stop

Owner: Codex implementation, independent internal reader review, existing
authorized publisher/integrator. Acceptance requires 25 local adversarial Git
tests plus the three actual-source distinctions above, repository checks and
privacy review, followed by actual authorized default integration/readback.
The current coordination suite automatically includes these tests in CI.
Baseline and rejected cases are not financial transactions or outside witnesses.

Observed October 15, 2026: the existing shallow checkout correctly rejected
all three actual-source inspections. A separate full public read-only clone
then accepted exactly PR125's four-file source, rejected PR124's extra protected
model path, and rejected the same-head stale-base case with the expected static
reasons above. No check was weakened to accommodate the shallow checkout.
Independent review also reproduced a worktree/include config gap in the first
implementation; the corrected effective-config read and two regression controls
close that gap. These are local integrity checks, not new payment experiments.

Bound: one offline safeguard and its tests, existing resources, zero spend,
signup, contact, signatures or chain operations. Stop on any false acceptance,
private diagnostic echo, unexpected mutation/network need, conflicting source,
or attempted authority expansion. It is not a new platform or sustained
integration-infrastructure lane. After this increment, return to the existing
buyer-qualified useful-work bottleneck and protected reconciliation owners;
do not rerun unchanged samples or create further generic helpers as progress.

AI analysis and implementation; not an offer or authority to pay, lend,
guarantee, recruit or transact.
