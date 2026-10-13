# nLine applicant access: source and decision limits

The employer's Field Surveyor listing advertises an October 23, 2026 application deadline and requires a CV and cover letter. Its application link resolves to the employer's Breezy application page, but an actual submission was not tested. The role requires residence in one of ten listed towns, suitable Android equipment, English, Krio and the local language, and availability for mandatory training.

Training is forecast for November 16–20, November 30–December 4, or December 7–11, with final details promised no later than three weeks before the start. The training venue remains undetermined. The published listing specifies 450 NLe per full training day, provided on the first day, while standard round-trip bus costs are provided on the last training day. Actual fieldwork remains conditional on performance and selection.

No particular applicant, transport cost, verified reimbursement eligibility, earnings, or incremental human benefit has been established. Do not interpret the published figures as guaranteed income. Existing project guidance prefers employer advances or direct booking, followed by no intervention; loans and guarantees are not authorized by this source check.

Source: https://nline-inc.breezy.hr/p/f933afb58414-field-surveyor (verified October 13, 2026).

## Offline consent and eligibility prescreen

`access_gate.py` checks applicant-provided boolean flags for explicit opt-in, employer-advertised residence, language, Android capability, open application status, CV, cover letter, and availability for mandatory training and possible fieldwork. Only the literal boolean `True` counts as consent; a string such as `"yes"`, `"no"`, or integer `1` is never accepted. Unverified or missing mandatory criteria fail closed. A favorable result allows only consideration of a voluntary application, not project outreach, recruitment, submission, funding, or a positive hiring prediction.

`first_day_cash_gap` calculates a provisional outbound-fare shortfall using decimal arithmetic; unknown, negative, nonfinite and boolean amounts are rejected. `classify_assistance` does not recommend credit: even a confirmed hypothetical shortfall merely points toward checking employer advance/direct booking before any independent sponsorship review. A hypothetical gap does not establish causation or permit payment. Do not assume advertised last-day bus funds or uncertain first-day per diems are already available before travel.

This module is an archival, in-memory, privacy-minimal safety prescreen, **not** an application service, financing mechanism, an employer-verified cost calculation or evidence of real informed consent. No names, contact information, identity documents, addresses, or payout credentials are collected. Do not enter participant details in GitHub. Under the agreed 2026-10-13 decision, the nLine path remains WATCHING until an independently consenting eligible person already applied by October 23 and supplies the required four evidence groups; do not contact or recruit anyone to manufacture that gate. If no such person appears by the deadline, archive this opportunity-specific route.

Run `cd experiments/nline-applicant-access-gate-20261013 && python3 -m unittest -v test_access_gate.py`. The 16 offline tests include rejection of truthy nonboolean consent, absent CV or cover letter, lack of training availability, unknown inputs and nonfinite monetary amounts. No network access, funded financial action, application, or outreach occurs.
