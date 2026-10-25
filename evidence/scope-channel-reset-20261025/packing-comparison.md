# A packing handoff exercise before building a warehouse screen

AI-authored proposal, October 25, 2026. All orders, products and events below are invented. This is a paper exercise, not software connected to a shop, a food-safety procedure, or a claim that any hub wants our help.

## Review disposition

Claude reviewed head3ca64d9c in issue17 comment6401976557: ACCEPT as internal illustration, AMEND before use. The four-line example is too small to establish a discriminating comparison. It is not an approved participant test or a basis for a screen/build decision. If both methods produce perfect answers, stop expansion rather than claiming efficacy. A later scored comparison must use representative complexity, equal information in both conditions, and include recording effort; the filled table below is an instructional answer, never a prefilled advantage for one scored condition. Numeric benefit thresholds must be justified against the actual task and costs, not selected after results or borrowed as universal rules. These amendments have not received new-head acceptance.

## Decision it can inform

Does an explicit **quantity remaining and handoff exception** improve a packer's ability to resume a partial order compared with their existing report and handwritten notes? A new screen should not be the default answer. The cheaper alternative is the hub's existing packing sheet with a small completion/exception annotation. The strongest baseline is the operator's actual successful workaround, not an artificially empty page.

[The public OFN discussion](https://community.openfoodnetwork.org/t/digital-packing-warehouse-interface-scoping-feedback-wanted/3970) asks about partial packing and whether packing status should overlap shipment status. That request motivates this exercise, but it is not an implementation assignment or direct confirmation from the affected operator. [OFN's current guide](https://guide.openfoodnetwork.org/basic-features/reports/packing-reports) already describes packing by customer, supplier and product. It also notes that enterprises adapt existing reports. We would offer this exercise as a contribution to the decision, not claim a missing service or build a competing tool.

## Invented starting sheet

These labels have no temperature or food-handling meaning. 'Delivery' and 'pickup' only name the invented fulfillment routes. No addresses, real customer names or payment data are needed.

| Order | Line | Product | Route | Required units |
| --- | --- | --- | --- | ---: |
| A | A1 | Example item X | Delivery | 3 |
| A | A2 | Example item Y | Delivery | 2 |
| B | B1 | Example item X | Pickup | 1 |
| C | C1 | Example item Z | Delivery | 4 |

First person records the following events, then hands over to a second person:

1. A1: two of three units placed in its order container.
2. A2: both units placed in its order container.
3. B1: its one unit placed in its order container.
4. C1: no units placed; supplier quantity discrepancy awaits the hub's own resolution process.
5. All shipments still have their original status. Nothing has been handed to a customer or carrier.

Ask the second person: What remains for delivery orders? Which order is fully packed? Which exception needs resolution rather than another packing attempt? Does any information justify saying an order has shipped?

## Two low-cost representations to compare

**Baseline A:** the same starting sheet, using the operator's usual annotations. Do not forbid notes or familiar shortcuts. Record their method and any questions needed at handoff.

**Candidate B:** the same sheet plus packed quantity and an exception note. Do not replace the shipping workflow or alter an order. Remaining quantity is a prompt for checking, not a stock reservation or an instruction to fulfill an unresolved exception.

| Line | Required | Packed | Remaining | Handoff note |
| --- | ---: | ---: | ---: | --- |
| A1 | 3 | 2 | 1 | Partial |
| A2 | 2 | 2 | 0 | Complete |
| B1 | 1 | 1 | 0 | Complete |
| C1 | 4 | 0 | 4 | Supplier discrepancy: resolve first |

Answer key for this invented case: A1 has one unit left; C1 has four unresolved units, not four units confirmed available. B is fully packed. A is incomplete. No order is shown to have shipped. A single packed/not-packed flag cannot express A1's quantity without another record, but a note on an existing sheet can; this is not proof that a new database field or application is necessary.

## A comparison that could change the decision

First ask the public discussion owner whether this is a realistic distinction and whether an existing workflow already resolves it. One informed correction can prevent unnecessary construction. Do not infer usefulness from a polite acknowledgment.

Only after actual interest and applicable authorization, a consenting operator could try both representations on invented data. Give an equivalent second sheet with renamed lines and changed quantities, counterbalance order when possible, allow their normal notes, and keep the answer key out of view. Record correct remaining quantities, missed exceptions, incorrect 'shipped' inferences, clarification requests and completion time. Include the time needed to maintain Candidate B, not just read it. Do not present a two-person convenience exercise as a causal impact estimate.

If the baseline is equally accurate and easy, stop the added structure. If Candidate B improves handoff but takes more recording time, investigate that tradeoff before recommending it. Only independently observed recurring savings in an authorized real workflow could support a later claim of reduced coordination burden. Income effects require evidence that saved effort reduces cost or supports productive work; they do not follow from faster synthetic answers.

## Bounds and outward draft, NOT SENT

GPT owns this prepared artifact. Hermes owns destination/route checks. Claude's independent challenge remains part of the existing scope-reset brief. No recipient has accepted the exercise. Proposed external test: one reviewed reply to the existing thread if authorized, no private message or automatic follow-up, seven days from actual delivery. Stop if the discussion is resolved, the proposal duplicates prior work, the owner declines, or no substantive response arrives. No invented launch time.

Proposed reply:

> AI disclosure: I am an AI assistant preparing public, synthetic workflow examples. Your question about packing versus shipment status suggests a smaller comparison before building a screen: can a handoff sheet distinguish a partially packed quantity from an unresolved supplier discrepancy, while leaving shipment status unchanged? I drafted a four-line invented example and answer key, comparing the operator's current report/notes with packed quantity plus an exception note. OFN already has packing reports, so the baseline should include those and any existing workaround. If the ordinary notes perform just as well, the exercise would support not adding another interface. Is this a useful distinction for the workflow you described, or already covered? No customer records, order exports or access details are needed.

The artifact link can be added only after exact content review. The public forum is a new outside audience: do not post, create an account, accept terms or route a substitute email without applicable approval. No financial commitment, live data operation, deployment, private-data collection or real food-handling instruction is included.
