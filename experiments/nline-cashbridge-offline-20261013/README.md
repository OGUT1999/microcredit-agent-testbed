# Conservative training-travel refund guard

This is a small, standalone input validator for the nLine Sierra Leone field-surveyor cash-bridge calculation. It rejects a hypothetical expected bus refund above the sum of the entered outbound and return fares, preventing a fictitious surplus in the cost model. It does **not** predict the employer's actual reimbursement or determine what travel legs qualify.

Run `cd experiments/nline-cashbridge-offline-20261013 && python3 -m unittest -v test_refund_guard.py`. Five tests cover exact, partial and zero refunds, over-refund, no-travel and invalid numbers.

Original employer listing: https://nline-inc.breezy.hr/p/f933afb58414-field-surveyor (checked 2026-10-13). Published deadline: 2026-10-23. The training town is still uncertain; the listing mentions bus travel to/from Freetown and payment on the last training day. Do not borrow or incur costs based on this model. A consenting applicant and actual spendable income are not verified.

The complete offline UI, cashflow engines and broader parity/browser tests remain in a locally generated bundle; this small module is **not** a substitute for integrating those exact files. Human-impact baseline stays $0. Source contains no applicant personal data or external calls. No recruitment, spending, guarantees or employer contact occurred.
