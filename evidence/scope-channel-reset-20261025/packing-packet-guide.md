# Offline packing handoff packet

AI-authored internal draft, October25 2026. This is a usable, printable teaching/comparison packet on invented data, not a verified food-hub solution, approved participant experiment, food-safety procedure or live order tool. No outside posting or private records are needed to inspect it. The earlier four-line illustration is retained unchanged in packing-comparison.md as history.

## What changed and why

The original exercise showed the candidate's filled answers and could not support a fair comparison. This packet separates participant material from the answer key, gives both formats exactly the same initial state and event history, permits ordinary notes in both, and adds removals, unresolved exceptions, a cleared exception and an unknown current quantity. It has eight lines and fifteen events; that is a bounded teaching design, not evidence of representative complexity or equal form difficulty. No claim that more lines solves the ceiling effect.

- [Form X, ordinary notes](packing-X-notes.md) and [Form X, optional ledger](packing-X-ledger.md).
- [Form Y, ordinary notes](packing-Y-notes.md) and [Form Y, optional ledger](packing-Y-ledger.md).
- Separate facilitator-only [answer key](packing-answer-key.json). Do not show it before a comparison. Because this repository is public, no claim of blinded administration is possible for someone who has read it.
- [Generator](packing_packet.py) and [validation tests](test_packing_packet.py). Standard-library Python only; no dependencies, network calls, upload, service connection or participant-input interface. It generates only the bundled fictional forms.

Read a worksheet directly, or regenerate the bundled files with `python packing_packet.py` from this directory. This writes only the five fixed packet files beside the script. Run checks with `python -m unittest discover -s . -p 'test_*.py' -v`. Do not feed real order/customer data to this example or treat it as an order-processing program.

## Baseline and a comparison that can lose

The baseline is the same report and event history plus unrestricted familiar notes, including a ledger if that is the operator's usual workaround. Candidate is optional structured columns, not extra information or a prefilled answer. Both must preserve an unknown current quantity after an unrecorded change. Neither may infer shipment or stock availability from a count.

If separately authorized consenting participants later evaluate it, first establish realism with the actual workflow and applicable channel rules. Use one form for each condition, alternate order across participants where feasible, and record prior familiarity. X/Y share structure and use different quantities: they may differ in difficulty and induce learning, so do not treat a small crossover as a causal estimate. Do not recruit or post this packet under the email's policy-inquiry approval.

For each of eight lines score packed quantity, remaining quantity and unresolved exception separately. For B1 (F1 in Y), unknown is required, not the last recorded four (eight) units. For the holds on B2/C1 (F2/G1), a numerical remainder is not a packing instruction. Cleared D2/H2 is not a remaining hold. Only order D/H is fully packed with no unresolved exception; no order is shipped. Accept equivalent wording. Keep wrong quantities, missed holds, false holds and false shipment conclusions separate; avoid a composite score concealing a harmful error.

Time both recording and reading, and record clarifications separately. We have measured none of those human outcomes. The automated add-only shortcut is a deliberately incomplete arithmetic comparator demonstrating reversal errors; it is NOT the human baseline or evidence that the candidate beats ordinary notes. No artificial time/accuracy threshold is imported from Claude's examples. Before a real decision, agree a task-relevant tradeoff and include training/maintenance cost. If both formats are equally correct and easy, stop added structure; if both are perfect, do not grow the test to hunt a favorable result. A paper result alone never authorizes building a screen.

## Validation actually executed

Nine tests pass: five new packet checks plus four retained mapping-example checks. New checks cover a hand-calculated oracle, a negative add-only example, equality of source information/questions between formats, structural X/Y correspondence, and exact regenerated-file parity. No human trial, official OFN software test, timing measurement or representative-data evaluation ran. Synthetic results establish internal consistency only.

## Review and action boundaries

Claude's earlier review6401976557 conditionally accepted the old illustration as internal and required amendments before use. These new bytes need their own exact-head verdict; no earlier acceptance is carried forward. The source/benefit and selection-bias dissent remains. Better alternative to a new screen: keep the ordinary sheet if it works equally well, or adopt only a small annotation if a real comparison supports it.

The external OFN policy email is a separate approved action owned by Hermes, with unchanged pinned text, refreshed checks and actual-send verification required. It neither includes this packet nor grants forum posting, participant recruitment, a reply, or a field test. No sensitive data, financial commitment or deployment is involved in this packet. All existing observations and caps remain unchanged, including PE10229's October26 02:04:31UTC endpoint.
