# Broader channels, bounded service tasks

Status: working decision and review packet, October 25, 2026. AI-authored by Codex. No external recipient has used this packet; no income or welfare effect is established.

## Decision and authority

Scott's direct instruction at 18:43:31 UTC was: "You are spinning.  Broaden scope and add channels." GPT adopts it now. It supersedes the passive A1 allocation and its external-object-only discovery restriction. It does not erase the useful lesson that an available bug or public dataset is not automatically an intervention worth pursuing.

We will investigate people-facing services, livelihood operations and humanitarian workflows in parallel. We do not need a personal invitation or guaranteed evaluator to investigate or prepare a reversible draft. We do need evidence, safe scope, actual contribution rules and applicable authority before sending or deploying it. Existing campaign caps survive. This is not a replacement controller, schedule, canonical queue or live-state update.

## Three paths and channels

| Rank | Path / owner | Concrete evidence and proposed test | Baseline / benefit hypothesis | Effort, window and decision | Kill / scale criterion | Authority and next step |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Service-delivery operations; GPT artifact, Claude technical challenge | A Kobo user asks how to diagnose mixed-version export labels. Prepare a synthetic example and a short read-only diagnostic reply; one task-specific forum response only if reviewed and authorized. | Existing Kobo documentation and support; less staff rework could improve service records. No school or household outcome inferred. | Preparation capped at 60 GPT minutes; proposed external observation 7 days from actual delivery, not running yet. | Stop if answered, unsafe, duplicate or no useful clarification within window. Consider another separately scoped task only after independent useful response, not views. | Local synthetic preparation allowed. Exact forum destination and sending identity need approval/verification. No access to user attachments or project. |
| 2 | Food-hub livelihood operations; Hermes channel/draft | Public OFN requests concern onboarding and packing workflow. Read current responses, identify one remaining question and prepare a task-specific response/artifact proposal. | Existing translated guidance/static reports; potentially reduce unpaid coordination or fulfillment errors. No buyer/payment or demand for us established. | Hermes requested output 19:25 UTC, max30 minutes; requested not accepted at packet creation. No external clock. | Stop duplicate advice or unsupported ownership. Scale only recipient-reported useful task completion. | No outward send/account creation now. Verify exact destination, norms, existing route, draft and authorization boundary. |
| 3 | Existing-service access; Claude challenge and practical aid | Compare one official-service navigation/process aid with a stronger alternative using existing benefits services and the prior research report. | Official calculators/advice already exist; an aid must reduce a specific burden without replacing eligibility assessment. | Claude requested output 19:25 UTC, max30 minutes; not an accepted SLA at packet creation. No external clock. | Stop duplication, individualized advice or unverified service access. Advance only a concrete usability comparison. | Public-source preparation and team review only; no beneficiary data, eligibility decisions or new invitation. |

These are research/preparation workstreams, not three launched experiments. GPT owns the final choice. Claude must pair each material challenge with a better alternative and a discriminating test. Hermes owns distribution within his actual permissions. Their actual outputs and acceptance, not these requests, determine completion.

## Concrete task: distinguish an export presentation issue from a saved-value mismatch

The public [Kobo support request](https://community.kobotoolbox.org/t/incorrect-school-to-ward-mapping-in-kobotoolbox-exports-after-moving-cascading-choices-to-external-csv-files/78408) describes inconsistent school/ward associations after external choice files and multiple form versions. We read the post, not its attached forms, files or submissions. The category listing showed one reply but the fetched topic showed only the initial post: response coverage is incomplete. Recheck before any approved send; do not claim unanswered.

A safe first answer should help separate hypotheses, not announce a root cause:

- Preserve originals. Do not edit submissions, identifiers or uploaded choice files as a diagnostic step.
- Compare stored codes with displayed labels in an authorized local copy. A surprising label alone does not establish a wrong saved choice.
- Keep form-version metadata with the local comparison and locate the matching historical choice definitions. Do not assume today's dictionary describes every older code, or that version metadata alone proves which external media bytes were used.
- If keys are reused, missing, duplicated or inconsistent with their parent, leave the case unresolved rather than silently assigning a label.
- Check export field selection separately from which submissions were collected under a version. The official advanced-export page is imprecise in its table, but its troubleshooting section explicitly says the all-versions option affects included fields, not a filter selecting only latest-version submissions. Use actual version metadata rather than inferring version from that checkbox.

The last point is documented behavior, not an independent live-platform test. If the requester finds their instance differs, the platform support owner should resolve it. We do not request private rows, school lists, screenshots, credentials, project links or exports.

## Executed synthetic demonstration

Run locally with Python's standard library:

```
python -m unittest discover -s evidence/scope-channel-reset-20261025 -p 'test_*.py' -v
python evidence/scope-channel-reset-20261025/synthetic_mapping.py
```

All four tests passed at packet preparation. Seven invented cases include a reused code across two versions, missing/unknown versions, unknown code, duplicate dictionary key and parent mismatch. Only two unambiguous examples receive labels; the other five remain unresolved. Inputs are unchanged and dictionary order does not break ties. A deliberately naive latest-dictionary lookup mislabels the old-version example.

This is a teaching example, not Kobo's algorithm, a reproduction of the requester's issue, a generic production validator or a data-repair tool. It accepts no files, uses no network and has no platform side effects. It demonstrates why a proposed diagnostic distinction matters; it does not show prevalence, saved labor, service quality or poverty impact.

## Exact draft for external review, NOT SENT

Destination: the existing Kobo support thread linked above, as one public reply to the request, only after current coverage, identity, forum norms and approval checks.

> AI disclosure: I am an AI assistant working on a poverty-focused public-service project. I have not opened your attachments or examined your submissions, so I cannot diagnose the cause. One useful distinction may be the export's field selection versus each submission's form version: Kobo's advanced-export troubleshooting says the all-versions option changes included fields, not which submissions are downloaded. Its data-viewing guide identifies `__version__` as form-version metadata. On an authorized local copy, compare saved codes, version metadata and the corresponding historical choice definitions before changing any data. If an old code is absent or reused in today's choice list, leave the mapping unresolved rather than guessing. I prepared a tiny, entirely invented example showing that failure mode; it is not a Kobo reproduction or repair tool. Would that distinction help you choose the next local diagnostic step? Please do not send records, attachments, school lists, screenshots or access details. Official references: https://support.kobotoolbox.org/advanced_export.html and https://support.kobotoolbox.org/viewing_validating_data.html .

A reviewed artifact link can replace the sentence about the example once its exact bytes are accepted and publicly readable. No send is authorized by this draft. Proposed cap: one reply, no automatic follow-up or private message; seven-day window from actual API creation if available, otherwise verified delivery timestamp. Success: independent recipient identifies a useful diagnostic step or a specific correction to our guidance. Acknowledgment, views and our own checks do not count. No response closes this bounded attempt without a no-demand conclusion.

## Sources and limits

- [Kobo advanced export](https://support.kobotoolbox.org/advanced_export.html), updated June 22, 2026, read October 25: field-selection distinction; wording conflict described above.
- [Kobo viewing/validation](https://support.kobotoolbox.org/viewing_validating_data.html), updated September 8, 2026, read October 25: form-version metadata. Not proof of external-file revision history.
- [External choices in XLSForm](https://support.kobotoolbox.org/select_from_file_xls.html), updated April 23, 2026, read October 25: choice identifiers and labels; external-file setup. We performed no upload.
- [OFN Spanish-support thread](https://community.openfoodnetwork.org/t/arg-new-agroecological-node-looking-for-spanish-support/4006), October 21: existing replies already provide translated guidance. Do not repeat it or assume the remaining link issues are unresolved.
- [OFN packing discussion](https://community.openfoodnetwork.org/t/digital-packing-warehouse-interface-scoping-feedback-wanted/3970), June 11: operator interest is reported by the author, not direct consent or a commission to us. Existing static reports are a baseline, not an absence of service.
- [Official UK calculator directory](https://www.gov.uk/benefits-calculators) and [MoneyHelper calculator](https://www.moneyhelper.org.uk/en/benefits/benefits-calculator): baseline services only, no individual assessment performed.

Existing observations continue separately, including the capped Moltbook intake through October 27 15:53:24.962 UTC. This packet does not consume, extend or replace its slots. No finance, accounts, deployment, private-data collection or outside message occurred during preparation. Protected live-write holds remain.
