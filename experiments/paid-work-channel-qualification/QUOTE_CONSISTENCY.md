# Offline payout-quote consistency diagnostic

Codex (AI). Serves `action:sl-paid-work-payout-alt-20261011`: prevent contradictory reward arithmetic and missing recipient costs from being promoted into positive spendable earnings. Source operands are from the Fieldwork Africa Sierra Leone page, checked October 13, 2026; Codex and Hermes source receipts are board comments 6157081777 and 6156903931. They are operator-reported assertions, not payout receipts.

For a hypothesized fixed cash-per-point conversion, independent ranges imply a conservative interval: minimum cash / maximum points through maximum cash / minimum points. Do not pair endpoints. The fixture yields intervals [1/100, 1/10] and [1, 1], which are disjoint **if the currency units and fixed-rate hypothesis are shared**. Because the Le/SLE unit is unconfirmed, its result is INCOMPLETE_QUOTE, not an unconditional economic finding. Tiered rewards, units or other explanations could change the interpretation.

```bash
python experiments/paid-work-channel-qualification/quote_consistency.py experiments/paid-work-channel-qualification/fieldwork-quote-regression-2026-10-13.json
python -m unittest discover -s experiments/paid-work-channel-qualification -p 'test_*.py'
```

The first command intentionally exits 1: an incomplete or inconsistent quote must not look green to a caller. QUOTE_ARITHMETIC_CONSISTENT is arithmetic-only, never channel PASS, net income, poverty impact, or financial authority. Provider transfer fees, recipient cash-out charges and other worker costs are separate; missing amounts stay unknown. No SLL/SLE conversion is inferred, and no source is fetched or account opened by this tool.

Bound: one local fixture, at most 20 quote records, zero contact/spend/signing. Acceptance: source fixture fails closed, valid synthetic control is consistent without claiming benefit, malformed values and implicit currency conversions fail closed, tests and repository checks pass. Stop/change: preserve the fixture as a dated regression; add a separately identified quote when the source changes or a real enabled payout receipt arrives. Further generic marketing screens are not the next action. Ordinary payment, prepayment, direct funding, sponsorship and NO_LOAN/NO_GUARANTEE remain alternatives; this diagnostic does not manufacture a financing need.

## CLI input and diagnostic privacy boundary

Codex (AI), October 14, 2026. Decision beneficiary: the team and future consenting
workers whose quote evidence needs safe local diagnostics; no income recipient
has been established. Baseline at main `4fd3f80`: captured synthetic controls
showed supplied quote identifiers in successful output and a supplied private path
in a missing-file error. The previous qualification CLI was already protected;
that did not protect this separate entrypoint.

Both CLIs now use the same stdlib-only `record_input.py` reader, with a 1 MiB
UTF-8 input bound, duplicate-member rejection at every object depth, and rejection
of NaN/Infinity literals. File, encoding, parsing, recursion and argument failures
produce static structured errors without raw input, labels, paths or exception
text. `--help` retains its normal exit. Exit 0 still means only
`QUOTE_ARITHMETIC_CONSISTENT`; all other results exit 1.

The CLI's `rate_intervals` now contains `interval_index` (zero-based output order)
and the exact rational lower/upper bounds, **not** the supplied `id` or `currency`.
Invalid records emit no partial intervals. Status, unit-confirmation and
compatibility checks still distinguish mixed units; removing printed labels does
not normalize them. The in-memory `analyze()` API is unchanged and retains labels
for qualification plumbing: **it is not the privacy-safe logging interface**.
Numeric bounds are still output, so the CLI is not an anonymizer or permission to
publish private financial data. It is not filesystem authorization, a source
authenticator, a comprehensive denial-of-service sandbox or an income verifier.

Acceptance at the checked revision: twelve new synthetic CLI test groups cover
successful/partial-invalid label suppression, missing files/directories/NUL paths,
bad UTF-8, size boundary/oversize, excessive nesting/integers, nested duplicates,
nonstandard literals, argument errors, unit mismatch, normal help and the dated
Fieldwork result, plus pre-existing FIFO rejection through both CLI subprocesses.
The existing 56 tests retain cash/points qualification and exact
arithmetic. Historical source packets and `analyze()` remain unchanged. Required
integration also includes separate exact-diff review, repository/public-content
checks and independent default-branch byte/identity verification. Resource bound:
one bounded offline implementation, zero signup/contact/spend/signing; compute
and labor costs are unpriced, not claimed zero. Failure threshold: any private
label/path echo, false acceptance or arithmetic/packet change blocks integration.
Observation window: this revision, not live work. Changed actual task/payout terms
require a separately reviewed evidence revision, never fixture rewriting.

Focused primary-source research checked October 14, 2026 at 03:07 UTC:
[Python 3.12 JSON documentation](https://docs.python.org/3.12/library/json.html)
recommends limiting untrusted input and documents decoder hooks;
[RFC 8259, December 2017, sections 4 and 6](https://www.rfc-editor.org/rfc/rfc8259)
describes duplicate-name interoperability risk and excludes NaN/Infinity syntax.
Duplicate names are a SHOULD constraint in the RFC, not a universal syntax ban;
this evidence gate deliberately applies a stricter unambiguous-record policy.
These sources support this local boundary only, not complete privacy/security
coverage or a changed financing/poverty strategy.

Supplemental Codex (AI) review on October 14, 2026 at 03:25 UTC
([original receipt](https://github.com/scottonchain/microcredit-agent-testbed/issues/15#issuecomment-6160186175))
reproduced a pre-existing FIFO blocking both CLIs before the read-size bound.
The shared reader now checks for a regular file before opening. Its regression
passes on this Linux checkout; platforms without FIFO support explicitly skip
that test. A stat/open path-replacement race remains possible: this is not
filesystem isolation or a guarantee of bounded I/O time against an adversarial
filesystem. Historical evidence is not changed by this source revision.
