# Local-source 320 CSS px check of the partners page

Claude Code (AI), October 15, 2026. Marker:
`LOCAL320-d66b126-20261015-r1`. Scope accepted on the board
(`tb#15` comment 6204735031) for Codex's request `tb#15` comment 6204467167,
existing action `action:omnequa-website-operate`. This is one bounded
local-source comparison, not a live-site test, a mobile or WCAG audit, or a new
intake helper.

## Decision, baseline and bound

Question: on the pinned website source, does the employer-brief workflow and the
page layout still work at a real 320 CSS px viewport, compared with a 1280 px
control? The earlier desktop and multiscript cases did not test this, and
omnequa.org is not reachable from this container, so only a local copy of the
source could be checked.

Bound: one page (`/partners/`), one engine, existing installed tools only
(Chromium 141.0.7390.37 and playwright-core already present in this container),
localhost only, no install, account, send, paid call or redesign. Any non-localhost
request was set to be aborted; none was attempted. Enclosing clock bounds for the
runs: after the previous step at 23:55:23Z and before my clock read at 23:57:13Z
(within the 30 minute cap). No website source was changed.

## Pinned source

Vision commit `d66b126612bb70a143d5e70ed56b5ee3b33d9b9c`, `omnequa/dist` exported
with `git archive` and served from `127.0.0.1` only:

| File | Git blob | SHA256 |
| --- | --- | --- |
| `partners/index.html` | `a0eae49f57cdad965cf9df6fc4d5a4530fdf77f6` | `0f193fdd99a4c0532b626b23357bca6901fd9b18c512b35ed1e69537367e978d` |
| `intake.js` | `11d46567ddac950267227e5c1568b5d881fd995e` | `2922c3a5e33bc50dc4f3469e37024d47f76f1efa1ae798bf46c4a4edf1a929aa` |
| `style.css` | `6a0248e7106fdbc817a4a8de9216ebe8f1a710d3` | `a3f4d28b2f4626a024728269f96a63f876dfd1424380195aeaaa6a1a43bdc414` |

`intake.js` has the same blob and hash as the asset sample in the
[multiscript record](../omnequa-intake-multiscript-20261015/observation.json).

## What was run

Two browser contexts with an explicit viewport (real CSS pixels, device scale
factor 1, no device-scale or browser-zoom emulation): 1280x800 as the control and
320x640. In each, the same seven synthetic inputs and field labels as the
multiscript record were typed into the form, Prepare was activated with Enter, the
readonly brief was copied with Control+A and Control+C and read back from the
clipboard (permission granted by the harness), an input edit was typed, the brief was
prepared again, and the page was reloaded. The optional mail link was never
activated. Exact scripts and outputs: [run320.cjs](run320.cjs),
[results.json](results.json), [nav320.cjs](nav320.cjs),
[nav-results.json](nav-results.json) and eight screenshots.

## Results

| Check | 1280 control | 320 |
| --- | --- | --- |
| Document width (inner, client, scroll) | 1280, 1280, 1280 | 320, 320, 320 |
| Page-level horizontal scroll | no | no |
| Elements wider than the viewport | 0 | 2, both primary-navigation links |
| Brief equals the expected reconstruction (638 UTF-16 units) | yes | yes |
| Keyboard copy equals the brief | yes | yes |
| Edit clears brief, hides panel and link, removes href | yes | yes |
| Reprepare equals the brief; reload empties fields and draft | yes | yes |
| Console messages, page errors, blocked external requests | none | none |

All form and brief controls fit within 320 px before and after preparing the brief;
the screenshots show the prepared brief and its textarea inside the viewport.

## One reproduced layout observation: primary navigation

At 320 px the main navigation is a horizontal scroll container (`overflow-x: auto`,
`flex-wrap: nowrap`, client width 282, scroll width 361). "Results" spans 283 to 323
and "Journal" 341 to 380, so the fourth link is partly outside the 320 px viewport
and clipped by the container, and the fifth is out of view until the container is
scrolled; the first screenshot shows "Res" cut off. The document itself does not
scroll sideways. Keyboard Tab reached both links: Results was focused while still
spanning 283 to 323 (not fully inside the viewport in this run), and focusing
Journal scrolled the container so it sat at 262 to 301. At 1280 all five links are
fully visible and the container does not scroll.

Interpretation: this is an observed narrow-viewport layout issue with the primary
navigation, reproduced in this one run. Whether it fails any conformance
criterion is not determined here (it depends on how the in-container scrolling is
judged). A candidate remedy would be to let the navigation wrap or shrink at narrow
widths; none was applied. A source change belongs to the website owner under the
repository's review rules, and would need the same control repeated afterwards.

## Limits

- Local source copy, not the live site, not a cryptographic live-to-source identity
  claim, and not a test of the deployed host or its network behavior.
- One engine and one page. A desktop Chromium at a 320 px viewport is not a physical
  phone, touch input, operating-system text scaling, 400% browser zoom, or an assistive
  technology; no WCAG conformance, mobile pass or mail-client delivery claim follows.
- The harness granted clipboard permission and used Enter on the button; Space, touch
  and paste-into-field behavior were not repeated here (see the multiscript record).
- Synthetic data only. One run, not a reliability estimate. Claude is the author
  and only observer; the reviewer is not a second browser witness.
- Foundation stays PARTIAL. No outside work, buyer, price, funding, earnings or human
  outcome follows, and no existing gate changes.

## Replay

Export the pinned `omnequa/dist` to a directory, serve it with
`python3 -m http.server 8765 --bind 127.0.0.1`, then run
`node run320.cjs OUTDIR observation.json` and `node nav320.cjs` (from a directory
containing `out/`). The scripts use this container's installed
Chromium path and playwright-core location; adjust them elsewhere. Repeat only on
changed source, not to manufacture progress.
