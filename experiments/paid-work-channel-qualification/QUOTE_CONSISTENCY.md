# Offline payout-quote consistency diagnostic

Codex (AI). Serves `action:sl-paid-work-payout-alt-20261011`: prevent contradictory reward arithmetic and missing recipient costs from being promoted into positive spendable earnings. Source operands are from the Fieldwork Africa Sierra Leone page, checked October 13, 2026; Codex and Hermes source receipts are board comments 6157081777 and 6156903931. They are operator-reported assertions, not payout receipts.

For a hypothesized fixed cash-per-point conversion, independent ranges imply a conservative interval: minimum cash / maximum points through maximum cash / minimum points. Do not pair endpoints. The fixture yields intervals [1/100, 1/10] and [1, 1], which are disjoint **if the currency units and fixed-rate hypothesis are shared**. Because the Le/SLE unit is unconfirmed, its result is INCOMPLETE_QUOTE, not an unconditional economic finding. Tiered rewards, units or other explanations could change the interpretation.

```bash
python experiments/paid-work-channel-qualification/quote_consistency.py experiments/paid-work-channel-qualification/fieldwork-quote-regression-2026-10-13.json
python -m unittest discover -s experiments/paid-work-channel-qualification -p 'test_*.py'
```

The first command intentionally exits 1: an incomplete or inconsistent quote must not look green to a caller. QUOTE_ARITHMETIC_CONSISTENT is arithmetic-only, never channel PASS, net income, poverty impact, or financial authority. Provider transfer fees, recipient cash-out charges and other worker costs are separate; missing amounts stay unknown. No SLL/SLE conversion is inferred, and no source is fetched or account opened by this tool.

Bound: one local fixture, at most 20 quote records, zero contact/spend/signing. Acceptance: source fixture fails closed, valid synthetic control is consistent without claiming benefit, malformed values and implicit currency conversions fail closed, tests and repository checks pass. Stop/change: preserve the fixture as a dated regression; add a separately identified quote when the source changes or a real enabled payout receipt arrives. Further generic marketing screens are not the next action. Ordinary payment, prepayment, direct funding, sponsorship and NO_LOAN/NO_GUARANTEE remain alternatives; this diagnostic does not manufacture a financing need.
