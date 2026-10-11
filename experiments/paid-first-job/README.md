# Paid first job: Stage A fill (proposed)

Status: **proposed** by Claude Code (AI agent), 2026-10-11, to fill the "next executable action" of
[paid-first-job-stage-a.md](../paid-first-job-stage-a.md). No one has been contacted and nothing
has been spent. Nothing here is approved: the cost card below goes to the operator, who alone can
approve posting, recruiting or spending.

## The work: listen to 20 quotations the blog published from video

Work class 2 of the packet (source-check of a published claim set), narrowed to the one check our
agents cannot do. The blog has published 20 direct quotations from four videos. Every one was taken
from YouTube's automatic English captions and checked only by AI agents reading those captions
(`microcredit-vision` `VERIFY.md`). Automatic captions mishear words, drop or repeat them, and do not
say who is speaking. Nobody has listened to the audio. A person who listens can confirm or correct
each quotation, its timestamp and its speaker. The result goes straight into corrections on the
blog, and it is verification by people outside the agent team, which the north star asks for.

Honest limit: in the last week the project would not have bought this check. It is real work with
real use, but small. The reservation value proposed below is set accordingly.

The 20 items, their exact published wording, listed times and speakers are frozen in
[items.json](items.json) (sha256 `9325412d2226dee20201122b455f3501c50e5f2ea59208c2c427899eb0819f19`,
pinned in the tests). All 20 strings were checked verbatim against the published posts at vision
`4f8a48f`. Political content is excluded: the one post that quotes a minister and the one that
quotes a White House event are not in the set.

| Set | Source | Items | Listed times |
| --- | --- | --- | --- |
| A | The Daily, "Call My A.I. Agent" (one episode) | 9 | none: the worker finds each quotation |
| B | Nonzero, The Cognitive Revolution, Doom Debates (three episodes) | 11 | yes, to the second |

Estimated effort: 60 to 90 minutes per set for a careful listener.

## Assignment: two sets, three workers each

Six contracts: three independent workers per set. Agreement among three listeners does not establish
what was said, so it decides nothing about pay and nothing about the blog. It only orders the
recheck queue: an item goes to a person on our side (the adjudicator) whenever any worker says
anything but EXACT or the workers differ, likely errors first. The blog is corrected only from
adjudicated items. The third check per set is quality control, so the project values each set once
(see the fair value line of the cost card).

## Exact job post

> **Title:** Listen to 9 to 11 short quotations in English podcasts and check them word for word
>
> We run a small public blog written by AI agents. It quotes podcast episodes that are on YouTube.
> Our quotations came from YouTube's automatic captions, and we need a person to listen to the
> audio and tell us whether each quotation is exactly what the speaker said.
>
> You get a list of 9 to 11 quotations, the video link, and (for most items) the time in the video.
> For each one, listen and fill in one row of a spreadsheet: what you hear, word for word; the start
> and end time; who is speaking; and one verdict: EXACT, MINOR (small wording difference, same
> meaning), MAJOR (meaning or speaker differs) or NOT_FOUND. If a quotation is not at the listed
> time, write what is said there instead and choose NOT_FOUND; for the episode without times, say in
> the note where you looked. Ignore um/uh, punctuation and repeated words. Expected time: 60 to 90
> minutes. No software beyond a browser and a spreadsheet.
>
> Fixed price $60, one milestone, due 5 days after the contract starts. One round of revision if a
> row is incomplete. We hire three people for the same list, but your pay never depends on whether
> the others agree with you. If you mark more than a quarter of the items NOT_FOUND, a person on our
> side listens to those items before we approve the milestone. Please do not use AI transcription; we
> already have the machine captions, and the point is a human ear.
>
> We are especially glad to hear from people new to the platform. Every completed contract gets a
> specific public review describing the work.

## Deliverable and acceptance (frozen, applied by [score.py](score.py))

One CSV per worker with the header `item_id,verdict,heard_text,start,end,speaker,note`, one row per
item. `start` and `end` are `h:mm:ss` or `m:ss`. A `NOT_FOUND` on a timed item needs what is said at
the listed time and a start within a minute of it; on an untimed item it needs a note saying where
the worker looked.

| Decision | When |
| --- | --- |
| ACCEPT | on time and every item answered in the required form; for a held sheet, also after adjudication |
| REVISE (once) | a row is missing or malformed (an unknown verdict, a blank transcript or speaker, an unreadable time, a span over two minutes, a start more than a minute from the listed time with no note, a NOT_FOUND without its evidence), or the adjudicator found two or more of a held sheet's NOT_FOUND items at the stated place |
| HOLD_ADJUDICATION | more than a quarter of the sheet is NOT_FOUND: the adjudicator listens to those items within 3 days of submission, before the milestone is approved |
| REJECT_INCOMPLETE | still incomplete after the one revision |
| REJECT_LATE | submitted after the contract deadline (an extension agreed on the platform before the deadline moves the deadline) |

Agreement with the majority and transcript corroboration (similarity of 0.85 or more to another
worker's transcript) are reported for every worker as quality measures. They never decide payment,
and no decision rests on peer disagreement. The adjudicator writes `adjudication.json` after
listening (or reading the publisher's own transcript where one exists); agents never write it.
`score.py` reads only worker codes (`W1` to `W6`); the mapping to platform accounts stays with the
operator and is never committed.

## Who is offered the job

Fixed before posting, so no one is picked by impression:

1. Eligible: the applicant's profile shows no completed jobs on the platform, the proposal is in
   English, and the platform's own identity checks are passed. Location and income are not used,
   and no one is labelled poor.
2. Applications close at a fixed time stated in the post.
3. Among eligible applicants, six are drawn at random: Python's `random.Random(seed).sample` over
   applicants sorted by application time, with `seed` the hash of a Base Sepolia block whose height is
   published before applications close. Only counts (applied, eligible, drawn) are published.
4. Workers 1 to 3 get set A, workers 4 to 6 set B, in draw order.

## The treatment, named

Prior evidence says what matters. In a randomized experiment on oDesk (now Upwork), hiring
inexperienced applicants for a short job with a public rating raised their later employment, and their
earnings over the next two months were about three times the control group's; the market-level
benefit exceeded the cost (Pallais, *American Economic Review* 2014). Verified experience helps
applicants from less developed countries most (Agrawal, Lacetera and Lyons, *Journal of International
Economics* 2016), and an intermediary's vouching lands newcomers their first job (Stanton and
Thomas, *Review of Economic Studies* 2016). The figures above come from search summaries; the paper
itself is blocked from this host and should be read before Stage B is designed.

So the treatment is **a paid, accepted contract plus a specific public review**, posted within 24
hours of acceptance. Template, filled from the scorer's output: "Checked N quotations against the
audio, found and documented M caption errors, delivered on time in the requested format. Careful,
precise listening." The project gives no review for rejected work and publishes nothing else about
the worker.

## Consent text (asked only after the work is paid)

> Thank you for this job. Separately, and only if you want: we are studying whether a first paid job
> helps people find more work. Over the next eight weeks we would ask you twice, briefly, how many
> new contracts or inquiries you got from other clients and what they paid. You can answer, skip, or
> stop at any time. Your payment and review do not depend on it. We never publish your name, handle,
> location or messages; we publish only totals across all participants.

## Cost card (for the operator's approval)

Figures marked *live* must be read from the operator's own account screens before approval. The
others come from public pages read on 2026-10-11 and may be out of date.

| Line | Amount | Basis |
| --- | --- | --- |
| Worker gross, 6 contracts x $60 | $360.00 | this packet |
| Client marketplace fee | $18.00 to $28.76 | 5% in several 2026 guides; Upwork's resource page "Is Upwork free" says up to 7.99%. *live* |
| Contract initiation fee | $0 to $89.94 | $0.99 to $14.99 per new contract in 2026 guides; can reach 25% of a $60 contract. *live* |
| **Maximum cash outlay** | **$478.70, cap $480** | sum of the maxima |
| Freelancer service fee (borne by worker) | 0 to 15% of $60 | variable, shown on each offer; record it per contract. *live* |
| Withdrawal (borne by worker, if reported) | from $0.99 | local bank outside the US, per the platform's payout page; method-dependent |
| Worker spendable, all six | about $300 to $354 | $360 less 0 to 15% and about $1 per withdrawal |
| Agent review time | about 1 hour Claude, 30 minutes Hermes | the scorer is automatic; agents cannot listen and adjudicate nothing |
| Adjudication (operator or another person who listens) | up to 60 minutes | about 3 minutes per recheck item, at most all 20 items; set A may be checked against the publisher's own transcript where one exists. **If no one can commit this time, the packet stays blocked** |
| Operator time | about 2 to 3 hours | client verification (once), posting, draw, six offers, six payments, six reviews |
| Fair value of accepted deliverables | $80 proposed | each set valued once at $40; the operator sets the reservation value |
| Incremental subsidy at the cap | about $400 | $480 minus $80 |

**What this says before anything is run.** At the cap, 62% to 74% of the cash reaches the workers as
spendable money ($300 to $354 of $480); with the lowest fees (5%, no initiation fee, $378 outlay) it is
79% to 94%. Direct cash transfers deliver more than 87%. The first job alone is at best comparable to
cash, and worse if the live fees are high. The experiment is worth running only for what follows it:
independent paid work that the first contract and review make possible. Stage B must therefore
measure follow-on contracts and earnings, not the first payment. Targeting is also weaker than a cash
programme's: new freelancers in any country are economically excluded from the platform's market,
but they are not screened for poverty, and the platform's identity and payout requirements will
exclude some of the poorest. Report both limits with the results.

## Proposed changes to Stage B (for the controller)

1. Name the treatment as above (paid contract plus specific public review), since that is the
   mechanism with causal evidence.
2. Follow-up window of eight weeks (Pallais measured about two months), with per-person counts of
   new independent contracts and their gross pay, self-reported with the platform's contract record
   as evidence.
3. Replace "at least 1 of 6 gets an independent inquiry" with a benchmark that can fail: if the prior
   evidence holds, most hires should get further work. Fewer than 2 of 6 with any independent paid
   contract within eight weeks is a stop signal for this route on this platform.
4. Report the cash-transfer comparison above with the results.

## Run the checks

```bash
python experiments/paid-first-job/score.py experiments/paid-first-job/items.json <submissions-dir>
python -m unittest discover -s experiments/paid-first-job -p 'test_*.py'
```

The tests pin the item file's hash, so changing an item is a new task that needs a new cost card.
