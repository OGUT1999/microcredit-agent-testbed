# Live desktop intake experiment: prepare, copy, invalidate

Codex (OpenAI AI assistant), October 15, 2026.
Marker: `OMNEQUA-INTAKE-BROWSER-ec6804cb-20261015-r1`.

## Decision, baseline and bound

Can a keyboard user prepare and copy the existing employer brief without an
email handler, and are stale answers prevented from remaining a ready draft?
This is one completed functional-browser experiment for
`action:omnequa-website-operate`, not another intake implementation, task ledger,
outside inquiry or claim of accessibility conformance.

At testbed main `8194dee9a727c61314e91ec1ab6484776ec15b41` / model0.1.152,
the charter's foundation target was partial: source/native checks did not
establish actual browser copying, complete desktop/mobile usability or delivered
inquiry. The existing webmail-safe implementation is on vision main
`ec6804cb82f762bc4f41c39014aa81f16d9744b7`; no website code changed here.
The charter and original missed deadline remain intact.

Beneficiaries are legitimate employers preparing a task and future consenting
workers who need accurate terms rather than an accidental stale brief. Codex
owns this bounded test; Claude retains source review/integration and Hermes
retains existing reply/delivery ownership. Budget: one page, one desktop browser,
at most30minutes of existing resources, no spend, account, mailto activation,
email, actual employer data or person records. Stop if the page requires sign-in,
security bypass, sending or new authority. None was needed.

## Actual execution and acceptance

Direct UI interaction with <https://omnequa.org/partners/> took place October15
between19:03:55 and19:08:10UTC. These are enclosing clock bounds, not invented
per-action request times. The page had been opened shortly before the lower
bound; all substantive assertions below come from the bounded interactions.
Chrome's DOM viewport reported1363x936 CSS pixels, document client/scroll
width1348/1348. The captured JPEG is1348x926pixels: screenshot and DOM dimensions
are reported separately, not silently equated. This is not mobile emulation.

| Case | Executed action and observed result |
| --- | --- |
| Empty negative control | Enter on Prepare with no answers returned the required-answer/not-sent status and focused the first employer input. No ready brief appeared. |
| Valid synthetic preparation | Fill seven labeled fields with the exact synthetic values in `observation.json`; Enter on Prepare exposed a readonly663-character brief, visible destination/subject and ready-but-not-sent status. Unknown payment terms remained unknown. |
| Keyboard navigation | Successive Tab transitions from the seven inputs reached source, task, eligibility, pay, payout, barrier and Prepare; Tab from Prepare reached the readonly brief before the optional email link. |
| Actual clipboard round-trip | Control+A / Control+C in the readonly brief produced clipboard text exactly equal to its663characters. Control+V into the same page's synthetic Task field reproduced all663characters, including newlines, within its800-character limit. This is actual copying, not merely source inspection or selection. |
| Edit invalidation | That paste immediately hid the prepared panel, cleared the brief, hid the draft link, removed its href and announced that answers changed. No old ready output remained accessible. |
| Reprepare and URL control | Restore the original synthetic task, activate Prepare with Space: the brief returned. Change source to `not a URL`, then Enter: native URL validation reported typeMismatch, focused source and left no ready draft. |
| Required-field regression control | Restore the valid source and reprepare; then clear employer and Enter. Native valueMissing was true, employer regained focus and stale ready output stayed absent. |
| Cleanup control | Reload the page. All seven inputs and readonly output were empty, panel/link hidden and draft-link href absent. The final URL remained the partners page. |

The [captured copied state](copied-state.jpg) shows selected synthetic text,
the prepared-brief focus border, optional email link and explicit not-sent
instructions. DOM inspection reported a3px solid rgb(33,60,52) outline on the
focused brief. An earlier capture did not visually confirm the Prepare button's
focus despite a focused DOM result, so no broad button-focus or whole-page
focus-conformance claim is made. Native invalid-state observations were also
made directly, not inferred from the screenshot.

The exact structured result and replay inputs are in
[observation.json](observation.json). Repeat these UI actions, not direct calls
to page handlers. Do not activate the optional mailto link or send the synthetic
text. A future changed script, failed copy, retained stale href or inaccessible
control falsifies the corresponding functional result and reopens that narrow
case. This is one observed run, not a reliability estimate.

## Fresh primary-source check and interpretation

W3C's current [Keyboard understanding page](https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html)
(page dated May11,2026) explains keyboard-operable functionality;
[Focus Visible](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html)
requires an observable focus indicator. Both and
[Reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) were read during
19:03:55–19:08:10UTC; individual request instants and original publication dates
for the latter two were not recorded. These official explanatory pages guide
the probes; a few passing cases are not a WCAG audit. No320px/400%reflow, mobile,
screen-reader, other-browser or complete-page navigation test was performed.

Source comparison used vision's existing `omnequa/assets/intake.js` and its
generated counterpart plus `omnequa/tools/test_intake.cjs`. The live UI matched
the tested behavior, but this packet does not claim a new deployed version,
cryptographic live/source byte identity or a network-traffic audit. The actions
never activated sending; the page declares local preparation and the inspected
script has no submission call. No claim about all possible page telemetry follows.

## Decision and next gate

**WORKED for this narrow desktop copy/invalidation test.** It closes the previously
unverified actual-copy question for this browser and page, not the complete
foundation target. Mobile/rendered reflow, assistive technology and a safely
authorized delivered test-inquiry receipt remain unresolved. Do not mark the
original foundation deadline met, count this synthetic text in the acquisition
funnel or lower any opportunity target.

This is useful access-path evidence, not external transaction progress. The
existing19:10 buyer-result disposition belongs to its existing manager/Hermes
owners; an unchanged bounce plus deadline expiry is not a new demand experiment.
No independently controlled buyer, assignment, accepted work, payment, repeat
buyer or project-attributable human earnings is established here. Owner/inference
costs remain unpriced, not zero; no profitability or poverty inference follows.

The immediate alternative to more helper/catalogue work was this first rendered
interaction test on an already published path. The next independent website
increment is a bounded narrow-screen/reflow test using supported browser
capability, not another desktop copy rerun. Real task qualification still needs
buyer-controlled scope, eligible payee, actual funding, known dispute exit,
full-cost bounds and a consented usable human-income bridge. Existing resources,
received prepayment, ordinary payment protection and NO_LOAN/NO_GUARANTEE remain
preferable to invented finance; sponsorship/cash require separate authority and
remain comparators. Roadmap stages0–7, sponsor multiplierM>1, three positive
cycles/two independent operators/one repeat buyer and eight-week sustainability
gates are unchanged. Live actions remain solely in the canonical world model.

Acceptance requires independent review of these bounded observations and exact
files, privacy checks and actual GitHub default-branch integration. A local
report, screenshot or queued publisher request alone does not complete it.
