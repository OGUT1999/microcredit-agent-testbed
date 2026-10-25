# Recorder-only invented packing exercise — form Y, ledger

AI-authored internal draft. Not an order, food-handling instruction or approved field test.

The first letter of a line ID identifies its order (for example, A1 and A2 belong to order A).
Each line begins with zero units packed and no exception. Required quantities stay fixed.
All shipments are unchanged and unshipped. There are no customer/carrier handoffs.
A numerical remainder is not evidence of stock availability. Unknown means do not guess.

## Starting sheet

| Line | Required units |
| --- | ---: |
| E1 | 10 |
| E2 | 4 |
| F1 | 8 |
| F2 | 6 |
| G1 | 12 |
| G2 | 4 |
| H1 | 6 |
| H2 | 2 |

## Event cards (same information in both conditions)

1. E1: place 8 units in the order container.
2. E2: place 4 units in the order container.
3. F1: place 8 units in the order container.
4. F2: unresolved exception: Supplier quantity disputed.
5. G1: place 6 units in the order container.
6. G2: place 4 units in the order container.
7. H1: place 6 units in the order container.
8. H2: place 2 units in the order container.
9. E1: remove 2 units from the order container.
10. G1: unresolved exception: Contents require operator check.
11. H1: remove 2 units from the order container.
12. H1: place 2 units in the order container.
13. H2: unresolved exception: Line identity disputed.
14. H2: exception cleared: Operator resolved identity dispute.
15. F1: Unrecorded change reported; present quantity not known.

## Working area

Optional structure; ordinary notes remain allowed. Fill from the same events.

| Line | Packed now or unknown | Remaining or unknown | Unresolved exception |
| --- | --- | --- | --- |
| E1 | ______ | ______ | __________________ |
| E2 | ______ | ______ | __________________ |
| F1 | ______ | ______ | __________________ |
| F2 | ______ | ______ | __________________ |
| G1 | ______ | ______ | __________________ |
| G2 | ______ | ______ | __________________ |
| H1 | ______ | ______ | __________________ |
| H2 | ______ | ______ | __________________ |

## Handoff questions

For each line record current packed quantity, remaining quantity (or unknown), and unresolved exception.
Which orders are fully packed with no unresolved exception? What establishes shipment?
Mark uncertainty explicitly. Do not resolve a supplier/contents question from this exercise.

Recorder time: ____  Reader time: ____  Clarification requests: ____
This sheet contains no answer key. Timing fields are blank, not measurements.
