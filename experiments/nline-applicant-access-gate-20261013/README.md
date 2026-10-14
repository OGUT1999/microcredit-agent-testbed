# nLine applicant access: source and decision limits

The employer's Field Surveyor listing advertises an October 23, 2026 application deadline and requires a CV and cover letter. Its application link resolves to the employer's Breezy application page, but an actual submission was not tested. The role requires residence in one of ten listed towns, suitable Android equipment, English, Krio and the local language, and availability for mandatory training.

Training is forecast for November 16–20, November 30–December 4, or December 7–11, with final details promised no later than three weeks before the start. The training venue remains undetermined. The published listing specifies 450 NLe per full training day, provided on the first day, while standard round-trip bus costs are provided on the last training day. Actual fieldwork remains conditional on performance and selection.

No particular applicant, transport cost, verified reimbursement eligibility, earnings, or incremental human benefit has been established. Do not interpret the published figures as guaranteed income. Existing project guidance prefers employer advances or direct booking, followed by no intervention; loans and guarantees are not authorized by this source check.

Source: https://nline-inc.breezy.hr/p/f933afb58414-field-surveyor (verified October 13, 2026).

## Offline consent and eligibility prescreen

`access_gate.py` checks applicant-provided boolean flags for explicit opt-in, employer-advertised residence, language, Android capability, open application status, CV, cover letter, and availability for mandatory training and possible fieldwork. Only the literal boolean `True` counts as consent; a string such as `"yes"`, `"no"`, or integer `1` is never accepted. Unverified or missing mandatory criteria fail closed. A favorable result allows only consideration of a voluntary application, not project outreach, recruitment, submission, funding, or a positive hiring prediction.

`first_day_cash_gap` calculates a provisional outbound-fare shortfall using decimal arithmetic; unknown, negative, nonfinite and boolean amounts are rejected. `classify_assistance` requires literal boolean `True` for both employer confirmation and actual worker-cost knowledge; truthy strings, numbers and containers fail closed. It does not recommend credit: even a confirmed hypothetical shortfall merely points toward checking employer advance/direct booking before any independent sponsorship review. A hypothetical gap does not establish causation or permit payment. Do not assume advertised last-day bus funds or uncertain first-day per diems are already available before travel.

This module is an archival, in-memory, privacy-minimal safety prescreen, **not** an application service, financing mechanism, an employer-verified cost calculation or evidence of real informed consent. No names, contact information, identity documents, addresses, or payout credentials are collected. Do not enter participant details in GitHub. Under the agreed 2026-10-13 decision, the nLine path remains WATCHING until an independently consenting eligible person already applied by October 23 and supplies the required four evidence groups; do not contact or recruit anyone to manufacture that gate. If no such person appears by the deadline, archive this opportunity-specific route.

Run `cd experiments/nline-applicant-access-gate-20261013 && python3 -m unittest -v test_access_gate.py`. The 25 offline tests include rejection of truthy nonboolean consent or confirmation flags, absent CV or cover letter, lack of training availability, unknown inputs and nonfinite monetary amounts. The existing repository entrypoint `python tools/check.py` now discovers this suite in a separate process. No network access, funded financial action, application, or outreach occurs.

## Bounded context-independent cash correction, October 14, 2026

Codex (AI) repaired the independently recorded synthetic failure in
[the immutable arena validation receipt](../../evidence/arena-inbound-3a8cf59c-20261014/validation.json):
same-unit fare `123.45` minus available cash `1.00` under caller precision 3
returned `122`, not `122.45`. The existing helper now uses a fresh explicit
44-digit context, with explicit rounding, exponent limits, clamp, flags and traps.
It does not change caller or mutable DefaultContext settings or flags. Supported
results retain the Decimal return type and significant trailing zeros.

Supported concrete inputs are strings, integers, finite floats interpreted as
their existing `str` decimal representation, and Decimal instances. Prefer exact
decimal text: accepting a float does not recover precision already lost upstream.
Inputs are intentionally bounded to 32 integer digits, 12 fractional places,
44 coefficient digits, and exponent -12 through 31. Text is at most 96 characters;
oversized integers reject before string conversion. Unsupported types/subclasses,
unknown, negative, nonfinite, malformed and out-of-bound values return None.
Excess trailing fractional zeros may exceed the scale bound; no rounding or
truncation makes them admissible. Bounded exponent notation remains supported.

Both amounts must already use the same verified unit; this numeric API does not
authenticate units, convert currencies, resolve NLe/SLE/SLL, verify actual costs
or establish financing need. Even a positive valid synthetic shortfall keeps the
employer-prepayment/direct-ticket-first classification, never loan authority.
[The correction receipt](../../evidence/nline-cash-context-20261014/README.md)
records source checks, acceptance limits, resource bound and next decision.
