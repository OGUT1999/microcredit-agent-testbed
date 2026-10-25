# Facilitator-only handoff controls and actual results

October25 2026. Invented controls, not participant observations. Three records were typed explicitly from the independently checked form-X oracle; they are not generated from the scoring function. Read each together with the blank reader-only starting sheet, never the event cards. Hold yes means an unresolved exception on that line, not permission to act.

The ordinary-notes baseline and optional ledger can both succeed. The negative control loses one uncertainty and incorrectly reuses the last known count. No claim about how often humans make that error is supported.

## Faithful ordinary notes

```text
A1 packed 3; remaining 2; hold no
A2 packed 2; remaining 0; hold no
B1 packed unknown; remaining unknown; hold no
B2 packed 0; remaining 3; hold yes
C1 packed 3; remaining 3; hold yes
C2 packed 2; remaining 0; hold no
D1 packed 3; remaining 0; hold no
D2 packed 1; remaining 0; hold no
```

## Notes with lost uncertainty

```text
A1 packed 3; remaining 2; hold no
A2 packed 2; remaining 0; hold no
B1 packed 4; remaining 0; hold no
B2 packed 0; remaining 3; hold yes
C1 packed 3; remaining 3; hold yes
C2 packed 2; remaining 0; hold no
D1 packed 3; remaining 0; hold no
D2 packed 1; remaining 0; hold no
```

## Faithful optional ledger

```text
A1 | 3 | 2 | no
A2 | 2 | 0 | no
B1 | unknown | unknown | no
B2 | 0 | 3 | yes
C1 | 3 | 3 | yes
C2 | 2 | 0 | no
D1 | 3 | 0 | no
D2 | 1 | 0 | no
```

## Executed result

```json
{
  "faithful_notes": {},
  "lost_uncertainty_notes": {
    "B1": [
      "packed",
      "remaining"
    ]
  },
  "faithful_ledger": {}
}
```

Both faithful records match; only B1 differs in the damaged record, in packed and remaining quantities. This is two cells on one line, not two affected lines or measured human errors. Scoring the known records requires no human judgment about numeric uncertainty. Exceptions are scored as present/absent here; this control does not validate human interpretation of exception wording, clarification effort or shipment questions.

Run `python packing_controls.py`. It reads only bundled constants and the synthetic answer function; it is not a general parser for participant data. Three new tests plus the existing nine pass (12 total). A contaminated reader fixture with appended event cards or facilitator answers is rejected. This is an exact-fixture check, not proof of universal semantic leak detection. The predictable X-to-Y mapping reproduces Y exactly; the guide therefore excludes it as an independent crossover form and selects one-condition/form-X-only design for any future separately authorized study.

Claude's alternative is adopted for separation and controls. We do not adopt a blanket ban on hold phrases/final numbers in every participant file: recorder source cards need the hold information, and required quantities can legitimately equal final quantities. The testable stronger boundary is that readers receive only reviewed blank source requirements and the recorder's detached record, never cards/key. This does not establish comparative human performance, demand, earnings or welfare, and does not authorize recruitment or outward distribution.
