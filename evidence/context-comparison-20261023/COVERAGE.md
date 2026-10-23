# Cash-coverage comparability: bounded public-evidence result

Codex (AI), 23 October 2026. Research supplement to PR371, not a country selection or field authorization. Draft awaiting the assigned source/decision challenge; no acceptance is inferred.

## Decision

**Close the published-table country-selection route without ranking Rwanda, northern Bangladesh or western Kenya.** This pass did not establish the requested common local denominator. Missing or inaccessible evidence is not low coverage, and the result does not establish that a suitably governed microdata analysis is impossible.

The next research decision is materially different: **use within-study, cost-matched comparisons to assess whether added services warrant their cost over cash**, before choosing a geography or designing another service. This is a research priority, not a claim that cash always wins or that a provider is accessible to us. Improving existing delivery remains the second alternative, conditional on a documented avoidable household burden and a cheaper effective remedy.

## Protocol declared before these reads

[Brief and requested Claude challenge](https://github.com/scottonchain/microcredit-agent-testbed/issues/17#issuecomment-6376404045). One public-table/questionnaire/metadata pass; no household records downloaded, account created, terms accepted or organization contacted.

Target: rural households in the **national bottom consumption quintile**, receiving **noncontributory cash social assistance during the previous 12 months**. Exclude private remittances, contributory pensions and in-kind-only benefits; mixed programs require identifiable cash receipt. Count recipient households once, not program enrollments. A household coverage denominator must not silently become a person-weighted denominator.

The geographic scopes were declared as rural Rwanda, rural Rangpur division in Bangladesh, and rural Siaya/Kakamega counties in Kenya. The latter two are explicit operational subsets of the earlier broad regional labels, not estimates for all northern Bangladesh or western Kenya. National quintiles are country-relative positions, not an equal international poverty threshold. Equivalence scales, quintile construction weights and uncertainty also need alignment or explicit sensitivity analysis.

## Identical five checks

| Check | Rural Rwanda, EICV7 2023/24 | Rural Rangpur, HIES 2022 | Rural Siaya/Kakamega, KCHS 2022 |
|---|---|---|---|
| Population and quintile | Cross-sectional dictionary provides rural residence and quintiles of real consumption per adult equivalent. A joint coverage estimate was not established. [R1] | Published local assistance table is not restricted to the poorest quintile. [B1] | Requested population/quintile intersection unverified; no substitute from a wealth index or older survey. [K1–K2] |
| Benefit types | Direct Support records money received; general income-support amounts combine cash and kind. An all-cash union needs a validated program crosswalk. [R1–R2] | Social security chapter covers cash and kind and includes pensions; its total cannot fill a noncontributory-cash cell. [B1] | Cash-only coding and exclusions unverified for the requested wave. [K1–K2] |
| Recall | Relevant income-support and Direct Support questions use 12 months. [R1–R2] | Table10.3 reports benefits over twelve months, but does not supply the required joint recipient count. [B1] | Unverified; do not borrow another wave's recall. [K1–K2] |
| Weights and denominator | Household and population weights are distinct in the dictionary. No joint weighted numerator, denominator or uncertainty calculated. [R1] | Sampling-weight method exists; table10.2 is household coverage across consumption levels, not the requested denominator. [B1] | Requested household weights and local joint denominator unverified. [K1–K2] |
| Local support and precision | Cross-sectional metadata supports household-population inference; subgroup precision not established here. [R3] | Rural division is a sampling domain; that alone does not establish precision of its poorest-quintile cash subgroup. [B1] | County coverage in older metadata cannot establish the requested 2022 rural-county subgroup's precision. [K2] |

### Primary source audit and decisive limits

**R1 — NISR cross-sectional documentation**, catalog119, public dictionary pp35–36 and44: household identifiers, residence, Direct Support money, consumption quintiles and weights are available as metadata. This is promising for a later analytical specification, not a computed coverage table. The dictionary's adult-equivalence measure must not be assumed equivalent to per-capita consumption elsewhere. [Public documentation](https://microdata.statistics.gov.rw/index.php/ddibrowser/119/export/?format=pdf&generate=yes).

**R2 — Original questionnaire**, PartE p70 (PDF page69), explicitly combines cash and in-kind amounts. PartD1 separately asks about Direct Support money. Participation or a latest-payment status alone is not the all-program cash-receipt numerator. Restricting the question to Direct Support could yield a different, narrower analysis; it would not answer total cash assistance coverage. [Blank questionnaire](https://microdata.statistics.gov.rw/index.php/catalog/121/download/1096).

**R3 — Sampling metadata**, catalog119, specifies selection-probability weights for the household-based population. This is the cross-sectional survey, not the separate VUP beneficiary frame. Neither metadata availability nor the beneficiary report establishes exclusion among the poorest households. [Sampling](https://microdata.statistics.gov.rw/index.php/catalog/119/sampling).

**B1 — BBS HIES2022 final report**, dated14 December2023: chapter10 tables10.1–10.4 and sampling section1.3.7 were inspected. Table10.2 gives rural Rangpur **47.7% household receipt of social security benefits**; it is deliberately not used as the target estimate. The chapter combines cash/kind programs and pensions. Table10.4 describes program composition among covered families, not the requested poorest-rural-household denominator. No multiplication of separate marginal percentages can recover that intersection. The rural-division sample and weighting discussion do not prove subgroup precision. [Official BBS-hosted PDF](https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-bbs/2024/12/22b6e770f6a84cd9a48ff636ae506818.pdf).

**K1–K2 — KNBS evidence limit:** the official2022 poverty PDF timed out. The public archive page and linked catalog123 were readable, but catalog123 is titled2021 and contains conflicting2020 dates/citation metadata. Its stated national/rural/county coverage is not evidence for a2022 joint cash-coverage estimate. This bounded pass therefore leaves all requested2022 measurement cells unverified rather than filling them with older or national figures. [2022 report](https://www.knbs.or.ke/wp-content/uploads/2024/10/The-Kenya-Poverty-Report-2022.pdf); [archive](https://statistics.knbs.or.ke/nada/index.php/catalog/central); [catalog123](https://statistics.knbs.or.ke/nada/index.php/catalog/123).

The closure is methodological, not a country score: even successful retrieval of Kenya's report would not repair the mismatched Rwanda/Bangladesh measures automatically. Reopening would require a concrete harmonized table or analytical specification with the five checks resolved, not another generic search.

## A different research decision, with constructive alternatives

**Challenge:** choosing an intervention from incomplete coverage statistics risks confusing absence of a transfer with an actionable delivery failure. **Better alternative:** compare cash and a specific added service within the same evaluated population at matched full cost. This can discriminate between mechanisms without pretending we know current local exclusion. **Test:** extract treatment contrasts, uncertainty, population exclusions, horizon and costing from existing head-to-head trials; reject extrapolation to a proposed population when the causal mechanism or baseline differs.

Two primary research objects have been opened for that next decision, rather than merely identified in search results:

- McIntosh–Zeitlin's April2022 workforce-study manuscript compares training with cash among poor underemployed youth. Cash improves several economic outcomes relative to cost-equivalent training; training has a business-knowledge advantage. The combined arm's interpretation is not simply that adding services always fails. This is historical trial evidence, not access to today's participants or a claim about all poor households. [Authors' manuscript](https://gps.ucsd.edu/_files/faculty/mcintosh/craig-mcintosh_usaid-workforce-readiness-program.pdf).
- Their November2023 nutrition manuscript, linked to the2024 publication by the author, finds that neither the studied program nor small cost-equivalent cash changed core child outcomes within a year; larger cash had different effects. Its method uses donor-cost matching and regression adjustment, not a universal cash benefit ratio. The next extraction must distinguish household receipts from donor expenditure and short-run from durable outcomes. [Authors' manuscript](https://gps.ucsd.edu/_files/faculty/mcintosh/mcintosh_cash-vs-kind.pdf); [author's publication index](https://andrewzeitlin.io/projects/2_cash_benchmarking/).

These are evidence cases, not a covert Rwanda country choice. Their advantage is a direct comparator. A stronger rival is that neither new cash nor our service is needed: existing provision may already dominate. The comparison must retain that baseline and the option of no project. Our involvement needs additionality over funding or improving existing provision, not just evidence that somebody else's intervention worked.

## Ranked research alternatives and boundaries

| Field | 1. Cash versus added livelihood/service components | 2. Improve existing delivery rather than add a program |
|---|---|---|
| Owner | Codex research; no field owner appointed | Codex research; existing program owners retain operations |
| Hypothesis | Cost-matched evidence can identify which component, if any, earns its extra complexity | A documented preventable household burden may be reduced more cheaply than expanding transfers |
| Specific test | Extract head-to-head trial contrasts and medium-term follow-up; later external test would compare a justified component with cash/existing provision | Specify a matched-period receipt/access-cost problem; later external test compares an authorized remedy with existing operations and cash |
| Baseline | Cash through an established provider, existing services and no new project | Current operational remedy, existing entitlements and cash alternative |
| Window/deadline | One bounded evidence extraction; Codex research decision by24 October22:00UTC, not a participant clock or another agent's commitment | Dormant pending concrete consequential-burden evidence; reassess at same research decision, no automatic repeated scan |
| Kill criteria | No incremental household outcome at matched cost, poor transferability, or existing provision dominates; do not build merely because evidence is interesting | Apparent issue explained by definitions, resolved, nonconsequential or cheaper existing remedy dominates |
| Authority/cost | Public research, zero spending/contact; no field launch | Public research, zero spending/contact; no access to program systems |
| Next action | Structured outcome/cost/horizon extraction, including a rival and disconfirming findings | Retain as rival; require specific aggregate burden and remedy evidence before further active work |

Neither is launch-ready. Provider availability, a locally appropriate population, a willing capable delivery partner, attributable added value, full costs, safeguarding and lawful data arrangements remain unverified. A field test would also require specific contact/data/financial authority as applicable. These are not a request for a vague budget or operator introductions; independent research can proceed while Scott's existing planning question remains unanswered.

## Review and preserved observations

Claude's requested23:20UTC source/decision challenge remains pending at this draft. The request requires a better alternative and comparison test for each substantive criticism, and explicit disclosure of unread sources. Prior context challenge6375941035 and subsequent correction6376279892 are delivered and closed; no new acceptance is inferred from them.

Active work is research only. Worksheet98b928ae observes through30 October01:39:36.834UTC (five attempts, substantive-error stop, no nudge/extension/second slot, Hermes replies). Core comment6360035485 observes through30 October07:42:16UTC (one comment, no nudge/repost). PR10347 observes through28 October12:39:18UTC under its existing owner and continuation gate. Other pilot privacy/case caps and closed routes remain unchanged. PR369/PR370 integration and protected live paths are untouched.

Actual adjustment: stopped the noncomparable public-table country-ranking route and selected within-study cash benchmarking as the next research decision. **No external experiment, participant use, income or welfare result occurred.**
