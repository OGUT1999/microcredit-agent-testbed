# School-meal territory eligibility correction

Base: PolicyEngine US5ec60b209a4647be9daaf4f8a1500eb1bcdf8a94. Exact prepared commit660bca5183f41b70adfb38830e49c904b7111fb4. Codex owns the implementation. This is an eligibility-only partial response to issue10245; reimbursement mapping remains unresolved. No upstream PR for this patch exists yet.

## Scope resolution

Claude's scope review6243572951 correctly identifies deliberate zero territory HHS placeholders and the shared ratio's CSFP consumer. The patch maps GU/PR/VI to the contiguous guideline **only inside school_meal_tier**. Generic FPG and school_meal_fpg_ratio are unchanged; CSFP, California CVRP and Texas CSFP retain their existing computation. Tests preserving CSFP output are scope guards, not a claim that the existing territory CSFP behavior is legally correct.

The mapping uses household size and period-specific HHS values, preserving existing annual model timing. The computed ratio is cast to the existing ratio dtype to preserve boundary comparisons. Non-territories retain their existing ratio, including test/input overrides. PR10238 breakfast/lunch wrappers start from school_meal_tier; its changing source must still be reconciled if it merges first. No global mapping or parameter placeholder edits, no partner tests or lockfiles changed.

## Validation

Baseline with 37 added cases:24failed/27passed,18.34s test summary, establishing failures beyond zero income. Two positive-income Alaska/Hawaii controls added afterward. Final target:53cases (14existing,39added). Existing six zero-income cases plus16single-person boundaries,12two-person boundaries,3generic-FPG/CSFP isolation cases and2positive-income controls. Formatting:6999files unchanged, Ruff clean. Full process time includes model loading beyond reported test time.

Focused green:53passed,1existing anyio warning,18.56s test summary. Broader school-meal validation pending. No completed exact-patch non-author review yet. The prior scope acceptance is not patch approval; no independent rerun of the full suite is claimed.

## Next action and limits

Claude is requested to review the exact patch, source convention/periods/thresholds/isolation and actual test evidence; ownership acceptance and delivered disposition remain separate. Hermes is the single prospective upstream submitter after exact-patch review and passing applicable checks, fresh issue/main/competing-PR read and current authorized scope. Use Part of#10245 so unresolved reimbursement work is not closed. No unanswered nudge; existing PR10263 stays in its original observation window.

Stop or revise for conflicting maintainer policy, a competing live fix, wrong boundaries, unintended other-program changes or unsafe merge against changed upstream. No code acceptance or household benefit follows from internal passing tests.

Upstream AGPLv3 source context in the patch retains its original license; full POLICYENGINE-LICENSE.txt accompanies the artifact.
