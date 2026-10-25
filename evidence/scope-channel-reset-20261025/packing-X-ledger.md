# Recorder-only invented packing exercise — form X, ledger

AI-authored internal draft. Not an order, food-handling instruction or approved field test.

The first letter of a line ID identifies its order (for example, A1 and A2 belong to order A).
Each line begins with zero units packed and no exception. Required quantities stay fixed.
All shipments are unchanged and unshipped. There are no customer/carrier handoffs.
A numerical remainder is not evidence of stock availability. Unknown means do not guess.

## Starting sheet

| Line | Required units |
| --- | ---: |
| A1 | 5 |
| A2 | 2 |
| B1 | 4 |
| B2 | 3 |
| C1 | 6 |
| C2 | 2 |
| D1 | 3 |
| D2 | 1 |

## Event cards (same information in both conditions)

1. A1: place 4 units in the order container.
2. A2: place 2 units in the order container.
3. B1: place 4 units in the order container.
4. B2: unresolved exception: Supplier quantity disputed.
5. C1: place 3 units in the order container.
6. C2: place 2 units in the order container.
7. D1: place 3 units in the order container.
8. D2: place 1 units in the order container.
9. A1: remove 1 units from the order container.
10. C1: unresolved exception: Contents require operator check.
11. D1: remove 1 units from the order container.
12. D1: place 1 units in the order container.
13. D2: unresolved exception: Line identity disputed.
14. D2: exception cleared: Operator resolved identity dispute.
15. B1: Unrecorded change reported; present quantity not known.

## Working area

Optional structure; ordinary notes remain allowed. Fill from the same events.

| Line | Packed now or unknown | Remaining or unknown | Unresolved exception |
| --- | --- | --- | --- |
| A1 | ______ | ______ | __________________ |
| A2 | ______ | ______ | __________________ |
| B1 | ______ | ______ | __________________ |
| B2 | ______ | ______ | __________________ |
| C1 | ______ | ______ | __________________ |
| C2 | ______ | ______ | __________________ |
| D1 | ______ | ______ | __________________ |
| D2 | ______ | ______ | __________________ |

## Handoff questions

For each line record current packed quantity, remaining quantity (or unknown), and unresolved exception.
Which orders are fully packed with no unresolved exception? What establishes shipment?
Mark uncertainty explicitly. Do not resolve a supplier/contents question from this exercise.

Recorder time: ____  Reader time: ____  Clarification requests: ____
This sheet contains no answer key. Timing fields are blank, not measurements.
