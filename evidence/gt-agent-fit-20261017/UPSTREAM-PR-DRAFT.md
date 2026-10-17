# Prepared upstream PR — not submitted

Title: Fix double-counted tips in Florida School Readiness income

Target: PolicyEngine/policyengine-us, main. Branch: fix-fl-school-readiness-tips.
Base: 5ec60b209a4647be9daaf4f8a1500eb1bcdf8a94.
Patch: 10cf9185357db18c801cf0a8957629c9ad49da40, exactly three files.

## Proposed PR body

Fixes #10262.

Florida School Readiness counted tips both within gross `employment_income` and as a separate `tip_income` source. Remove the separate source so $30,000 in gross annual wages including $10,000 in tips produces $2,500 monthly countable income, rather than $3,333.33. Add paired YAML cases with and without separately reported tips, plus a changelog fragment.

Validation: the tipped regression fails before the correction (six pass, one fails) and all seven countable-income tests pass after it. The Florida School Readiness folder passes 126 tests in 17 files across six sequential isolated batches (376.2 seconds, maximum reported batch RSS 2170 MB). `make format` passes; no partner tests or dependency lockfiles changed. The complete upstream suite was not run.

axiom: needed

Prepared by Codex (AI), with human authorization required before submission. Non-author review status must be filled from the actual delivered review; it is not yet complete.

## Delivery checklist for the authorized execution owner

- Record Scott's specific approval receipt before any fork, push or PR submission.
- Recheck current issue, main, open PRs and ownership; stop for a competing fix or live owner.
- Verify non-author code-review disposition against the exact patch. Strategy/process review is separately tracked and is not an automatic code-review prerequisite.
- If base changed, assess the diff; changed patch semantics require focused revalidation and reviewer disposition, not automatic reuse of old approval.
- Publish the exact three-file patch with explicit noreply author and committer through authorized credentials; no paid encoder, dependency change, partner test edit or policy expansion.
- Read back PR head, contents and author/committer identities. Start the seven-day observation window only on actual submission. No unanswered nudge.
- A submitted PR is not acceptance, deployment, usage or household benefit. Preserve maintainer review authority.
