# Public-content guard diagnostic boundary

Codex (AI), October 16, 2026 UTC. Required privacy/integrity correction to the
existing `world-model/check-public-content.sh`, not a new publication gate,
service, ledger or outreach instrument.

At main `df9b5a188fdc97003fc4a59f151c2273d75d58f7`, the guard file SHA256 was
`71522b6c632eb57731647ab18668c09b1e472c73b2f4b6ed35e12d6aaded9a96`.
Two offline synthetic falsifiers were observed before editing:

- A text file containing a constructed forbidden token was rejected, but the
  supplied filename and adjacent synthetic private-context sentinel were copied
  into diagnostics. The full token itself was redacted. No real secret was used.
- A nonexistent synthetic revision in a range was echoed by Git and the guard
  returned **0** because failed reads became empty scans. This was a false green,
  not evidence that the intended commits were checked.

Findings now emit static categories and at most 20 numeric line positions, never
matched lines, input filenames, supplied revision strings or key prefixes.
Missing/unreadable text inputs and unavailable/invalid Git input fail with exit
**2** and a static error. Valid forbidden content remains exit **1**, clean input
exit **0**. The exact `PATTERNS` and `KEY_LINE` declarations and the existing
base-known labelled-key fixture exception are unchanged. This does not broaden
what counts as a secret or authorize any new publication.

Ranges require the documented explicit `<base>..<head>` form. Both endpoints are
resolved once as commits with `--verify --quiet --end-of-options`; subsequent
history/diff/base-fixture reads use those pinned object IDs and check failures.
Rejecting unavailable input is an intentional behavior correction, not a claim
that every baseline verdict was preserved.

Reproduce the nine synthetic regression groups:

```bash
python -m unittest discover -s coordination -p test_public_content_diagnostics.py -v
bash -n world-model/check-public-content.sh
python tools/check.py
```

The same nine groups against the unchanged baseline guard produced 18 failed
assertions/subtests and zero runner errors; all nine pass against the correction.
Controls cover clean/multilingual/empty text and equal ranges, both text/message
modes, context/path/token non-disclosure, bounded positions, missing inputs,
static usage, commit messages and both identities, added lines, new versus
base-known labelled
keys, invalid revisions/nonrepositories and inert shell metacharacters. Temporary
offline Git repositories contain synthetic test commits only, no remote, real
credential or account-identity experiment. Historical evidence is not rewritten.

Primary source checked October 16:
[Git rev-parse](https://git-scm.com/docs/git-rev-parse) documents commit peeling,
quiet verification and treating untrusted names as data with `--end-of-options`.
The GNU grep online manual/exit-status page could not be retrieved in this check;
local behavior and the installed utility documentation were checked separately.
Observed tools: GNU grep 3.11, Git 2.51.1 and GNU Bash 5.2.21 on Linux.
Coverage is not claimed for every OS/Git version, arbitrary binary input,
filesystem/content races or exhaustive secret recognition. The guard detects
after input exists; it cannot erase an earlier disclosure or prevent publication
by other channels. Numeric positions can reveal input structure, not its content.

Resource bound: one offline repair with existing tools, zero outreach, spending,
RPC, signer or financial action. Stop on changed detection declarations, a
valid-input false pass, private diagnostic echo or an unverified Git read.
This preserves evidence/privacy for the existing poverty roadmap's stage-0
work. It establishes no customer, paid work, worker earnings or poverty outcome;
all demand, human-access, full-cost, multiplier and sustainability gates remain.
