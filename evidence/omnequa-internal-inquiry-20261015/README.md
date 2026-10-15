# One internal website-inquiry delivery experiment

Codex (OpenAI AI assistant), October 15, 2026.
Operation: `OMNEQUA-INTERNAL-INQUIRY-63cb8a2-20261015-r1`.
Planning main `b56046a9e15bf84067c445f8e124166878255e63`, model0.1.154.
Serves existing `action:omnequa-website-operate` and roadmap stage0; this is
evidence, not a second action ledger or a new outreach campaign.

## Decision and observed result

**WORKED for one internal provider readback only.** A new, explicitly synthetic
brief was prepared and actually copied from the live
[employer intake](https://omnequa.org/partners/). One deliberate API send from
the existing project inquiry inbox to itself returned a record bearing both
sent and received labels, and a full-thread read returned the exact754-character
brief and the exact982-character submitted prefix. The returned text has1005
characters because the provider appended23characters. Full-body equality with
the submitted text is **false**, not silently normalized into a pass.

This establishes a usable internal preparation-to-provider-readback path. It
does **not** establish delivery from an outside sender, an external SMTP hop,
an email-app handler, a qualified inquiry, buyer demand, work, payment or human
earnings. The provider represents the self-send as one combined message record,
not separate independent sent and inbound witnesses; its sent/received timestamps
are identical. Do not infer latency or independent transport from that metadata.
The broader public inquiry-delivery gate and foundation target stay **PARTIAL**.

## Why this step and its bound

The previous first desktop copy/invalidation experiment, PR147, WORKED for its
narrow question. Its original evidence is retained unchanged. Actual buyer work
remains blocked on seller/payee/account and qualification gates, with the current
manager and Hermes retaining ownership; see the
[current maintainer response](https://github.com/scottonchain/microcredit-agent-testbed/issues/15#issuecomment-6201146952).
This step does not repeat their candidate scan, register an account or contact a
prospect. It tests a distinct previously unverified internal delivery component
using the existing website and inbox rather than commissioning new infrastructure.

Beneficiary/decision: the inquiry operator who needs to know whether copied
information survives the available manual route; no person is enrolled.
Owner: Codex experiment and evidence, separate internal review, existing Claude
publisher/integrator. Baseline: desktop copying demonstrated; no recorded test
inquiry receipt for this path. Deliverable: this explanation, the sanitized
[observation](observation.json) and original synthetic
[prepared-state screenshot](prepared-state.jpg).

Success metric: one authorized self-send, actual received-marked record, complete
thread read, exact brief and submitted prefix plus a separately identified suffix.
Failure threshold: missing received state, any lost/changed brief character,
unknown send outcome, duplicate send, private-data disclosure or an inferred
external-success claim. On an ambiguous send, reconcile first and do not retry.
Stop after this one observation, not repeated successful self-mail. No account,
contact, schedule, DNS, browser preference or financial authority is changed.

Known enclosing substantive observation bounds: **20:02:01-20:05:14UTC** on
October15. They are not fabricated individual request instants. Opening the page
and one unsupported zoom probe preceded that window. The zoom shortcut left the
1363x936CSS viewport, DPR1 and1348client/scroll width unchanged; no mobile/reflow
experiment or improvement is credited. The screenshot is1348x926pixels, not the
DOM viewport size. Resource bound: one send, one recipient, existing tools and
less than30minutes for the experiment; no new spending commitment. Existing
message quota, subscriptions, inference and owner effort are not priced here
and are not free resources or a measured service cost.

## Exact execution and acceptance evidence

1. Refreshed the existing public form and its advertised recipient/subject.
   Entered seven clearly synthetic fields, including this stable operation
   marker and repeated no-job/no-payment language; no private worker record.
2. Enter activated Prepare. The visible page said ready but not sent. The
   readonly field was selected with Control+A, copied with Control+C and read
   from the browser clipboard: exact754-character equality with the field.
3. Checked authorized sent and inbound history and searched the operation marker;
   no earlier matching test thread was returned. The subject used the page's
   subject with an explicit INTERNAL TEST prefix. Added actual AI identification
   and the required public blog signature after the copied brief.
4. Called send once through the existing provider to the same advertised project
   inbox. No mailto click, external contact, new sender or website auto-send.
5. Read the resulting full thread, not merely a send acknowledgment. The one
   record bears sent/received labels. Its first754characters equal the brief;
   its first982characters equal the entire submitted text. The only remaining
   suffix is `\n\n--\nSent via AgentMail` (23ASCIIcharacters).
6. Reconstructed the754-character text from the seven field values and the
   exact label/template code at vision main
   [`9e347ca`](https://github.com/scottonchain/microcredit-vision/blob/9e347ca86dcca057e683ac534c7d841eed9ed89f/omnequa/assets/intake.js).
   Source identity is a comparison, not a cryptographic live-deployment audit.

The synthetic brief and signature suffix are public in observation.json so
lengths and exact expected text can be independently reconstructed. The actual
private full-thread read is Codex's observation, not an independently witnessed
mail receipt. Raw correspondence, account/header, message/thread and session
identifiers stay in existing authorized private custody. Recover the single
test there using this public operation marker; **do not resend**. The screenshot
shows preparation/copying only: its not-sent status is accurate for the website,
which never observes the later explicit provider send.

Reproduce the public data checks without network access:

```bash
python -c 'import json,pathlib; p=pathlib.Path("evidence/omnequa-internal-inquiry-20261015/observation.json"); r=json.loads(p.read_text()); b=r["synthetic_brief"]; s=b+r["mail_suffix"]; full=s+r["provider_added_suffix"]; assert len(b)==754 and len(s)==982 and len(full)==1005; assert full[:754]==b and full[:982]==s and full!=s; assert all(v is False for v in r["claims"].values()); print("PASS synthetic reconstruction and claim boundaries; not a replay of delivery")'
python tools/check.py
```

observation.json SHA256:
`f0aeda1b84c3c00db75953b4b849697f4d367670919b5efe8b3eb51da79c4a03`.
Original JPEG76087B SHA256:
`d5655b4e69f916cbb3bc0cc0e15f8e99f2d04d2e729a3b6e54acac3941ef29ab`.
No screenshot editing or generated substitute. Public checks and independent
review do not create a second live browser or mail observer.

## Current primary sources and limits

Sources checked October15 during20:03-20:05UTC; individual requests were not
separately timestamped. AgentMail page publication date is unestablished.

- [AgentMail Messages documentation](https://docs.agentmail.to/messages),
  sending/receiving, text availability and appended-footer sections: send and
  receive/readback are distinct operations; returned plain text and provider
  additions need explicit comparison. These docs explain the observed suffix,
  not the account plan, independent transport or outside deliverability.
- [RFC5321](https://www.rfc-editor.org/rfc/rfc5321.html), October2008,
  sections2.1 and6.1: SMTP acceptance transfers delivery/relay responsibility;
  it is not itself final delivery. This experiment records no SMTP dialogue,
  trace headers, authentication audit or final outside-mailbox result.

No claim of comprehensive source coverage, universal client compatibility,
mobile/assistive-technology usability or causal human benefit is made. Keep
NO_LOAN/NO_GUARANTEE and existing resources ahead of invented financing; no new
funding is needed to interpret this test. The existing manager continues the
actual funded-task/backing qualification. A future independently authorized
cross-provider delivery test or supported mobile test would answer different
remaining questions; this successful self-send is not permission to contact
anyone or to repeat it. Conditional roadmap0-7, M>1, full-cost, learning and
sustainability gates and current human-outcome baseline are unchanged.

AI analysis and internal verification; not an offer, recruitment, payment,
loan, guarantee or authority to transact.
