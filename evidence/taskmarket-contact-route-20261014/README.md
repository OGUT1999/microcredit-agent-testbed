# Existing buyer inquiry: DNS-layer qualification

Codex / ChatGPT (AI), October 14, 2026. One <=15-minute, zero-contact,
zero-spend desk check for `action:agent-commerce-buyer-result-20261015`.
Read canonical main `ff771f1`, model 0.1.139, then exact source PR120
`06237c4b03c28dec20b07ffdb013c414d9b3aac2`, model 0.1.142. No new prospect,
account, SMTP session, test message, nudge, webhook or delivery service.

Decision served: avoid mistaking unconfirmed delivery for buyer refusal, or
using a working website/DNS response to claim a working buyer conversation.
Hermes retains sole reply/STOP ownership; Claude retains the existing operator
seller/payee decision and r2 response. Neither is inferred from these reads.

## Observations

The existing [public profile](https://taskmarket.dev/agents/63859) still advertises
a questions-first route at 21:54:31.391216 UTC (249,891-byte HTML, SHA256
`3de11632a4052f0bca5de70038819773397ebfd6847ede759b0082c3348d1222`).
The mailbox address and private correspondence are deliberately not copied.
Current authorized read of the single inquiry still finds sent/delayed and no
received reply. Public owner receipts [6178622378](https://github.com/scottonchain/microcredit-agent-testbed/issues/17#issuecomment-6178622378)
and [6178947911](https://github.com/scottonchain/microcredit-agent-testbed/issues/15#issuecomment-6178947911)
retain the actual inquiry/checkpoint facts.

[dns-observations.json](dns-observations.json) preserves 16 public DNS-over-HTTPS
responses, including original UTF-8 text, byte counts, SHA256, parsed data and
actual read times, 21:58:43.210296–21:58:48.296594 UTC. Google and Cloudflare
resolvers both report these three MX records for `taskmarket.dev`:

| Preference | Mail target | Address observation from both resolvers |
| --- | --- | --- |
| 26 | route2.mx.cloudflare.net | Three A and three AAAA records |
| 26 | route3.mx.cloudflare.net | Three A and three AAAA records |
| 42 | route1.mx.cloudflare.net | Three A and three AAAA records |

All 16 responses have DNS status 0. Neither resolver returns a null MX or an
empty MX set; the targets have address records. These are two resolver views
of the SAME DNS zone, not two independent witnesses of buyer identity, intent
or delivery. The captured responses are not claimed DNSSEC-authenticated.
Domain A records were also retained, but are not substituted for the explicit
MX targets. Public target addresses are observations, not connection probes.

## What this does and does not resolve

[RFC5321 section5.1](https://www.rfc-editor.org/rfc/rfc5321#section-5.1)
distinguishes explicit MX routing from implicit host-address fallback when MX
is absent. [RFC7505](https://www.rfc-editor.org/rfc/rfc7505) defines null MX as
a domain's declaration that it accepts no mail. Neither condition was observed
here. A healthy DNS layer alone does not establish SMTP or mailbox acceptance.

[Cloudflare's routing documentation](https://developers.cloudflare.com/email-service/configuration/email-routing-addresses/)
describes address/Worker rules, verified destinations, disabled rules and drop
actions. We cannot infer which rule or forwarding destination this domain owner
configured. No dashboard, account or destination mailbox was inspected. **The
cause of the existing delay remains NOT_DIAGNOSED; delivery remains UNKNOWN.**

| Observed fact | Unproved next layer |
| --- | --- |
| Public questions-first route | Active alias/destination and recipient consent to a deal |
| MX and target addresses present | SMTP acceptance, forwarding and mailbox receipt |
| Sending API accepted; sent/delayed | Delivered event, actual reply or terminal diagnostic |
| A reply, if it arrives | Assignable paid scope, funded acceptance, authorized payee and net income |

## Acceptance and stop/change conditions

Acceptance checks: all stored raw byte counts/hashes match; both MX sets agree
after normalizing trailing dots; each of the three targets has A and AAAA answers
from both resolvers; status and limitations are preserved. Reproduction is a
fresh ordinary GET to each saved URL, accepting `application/dns-json` for
Cloudflare. TTLs and response hashes may change; do not rewrite this snapshot.
No SMTP authentication, VRFY, recipient probe or message is part of reproduction.

Stop at this named-domain/DNS bound. Reopen only for changed public routing or
an actual delivered/failed diagnostic, reply, or authorized owner correction.
Hermes's existing Oct15 07:10/19:10 UTC checkpoints remain; no additional timer,
channel or resend. A missing reply at the deadline is NO_CONFIRMED_DELIVERY for
this inquiry, not global venue unavailability or buyer refusal. Retain the
accepted truthful-scope and payee gates; current recommendation is provisional.

NO_LOAN stays the default: financing cannot establish contact, fair acceptance
or an authorized payee. Prepayment/escrow may help a genuinely assigned job;
sponsorship, direct funding and a revolving guarantee need separate evidence and
authority, not a technical delay. Human contribution, consent, spendable lawful
payout, full costs, counterfactual earnings and harms remain unestablished. No
paid assignment, customer revenue, human earnings or poverty effect results
from this diagnostic. Earlier custody, calibration and outside commitments stand.
