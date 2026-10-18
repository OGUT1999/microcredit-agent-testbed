Part of #10245 (income eligibility only; territory reimbursement mapping remains open).

Use the contiguous-state income guideline when selecting school-meal tiers for Guam, Puerto Rico and the Virgin Islands. Deliberate zero territory entries in generic HHS guidelines previously produced undefined/infinite income ratios and PAID tiers below the free/reduced thresholds.

The correction stays inside school_meal_tier. Shared school_meal_fpg_ratio, generic poverty guidelines and CSFP/other consumers are unchanged. For GU/PR/VI, the territory branch recomputes from income and size even if school_meal_fpg_ratio is directly supplied; other states retain the existing input behavior. No CSFP policy determination or reimbursement fix is included.

A separate school_meal_tier_territories.yaml contains35cases covering zero income, both thresholds and the next dollar for one-/two-person units, and stable Florida/Alaska controls. Existing test files are untouched. This avoids conflicting appends with openPR10238 and avoids assertions that would freeze the existing CSFP error.

Current-main revised-file validation:35passed. PR10238 merge tree55819d3b plus this patch also passes35cases and merges cleanly. Exact revised-patch non-author review remains pending; record its actual disposition before submission. Prior53/118pass results apply to the superseded test set. Full upstream suite/CI not run. Formatting and whitespace checks pass.

axiom: needed

Prepared by Codex (AI), with authorized single-owner submission by Hermes after exact review. The submitter must identify itself; no private household records or financial commitment.
