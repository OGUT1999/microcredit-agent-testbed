Part of #10245 (income eligibility only; territory reimbursement-rate mapping remains open).

Use the contiguous-state income guideline when selecting school-meal tiers for Guam, Puerto Rico and the Virgin Islands. Their generic HHS guideline entries are deliberate zero placeholders, which previously made the school-meal ratio NaN or infinite and selected PAID even below the free/reduced thresholds.

The correction is local to `school_meal_tier`. It leaves `spm_unit_fpg` and the shared `school_meal_fpg_ratio` unchanged, because CSFP and other programs consume them. It does not determine CSFP territory policy or repair reimbursement rates. PR10238's evolving school-meal coverage must be reconciled if it lands first.

Tests cover zero income, both thresholds and the next dollar for one- and two-person units, non-territory controls, and unchanged generic-FPG/CSFP behavior. Baseline expanded target:24failed/27passed before the correction; final target53passed (two positive-income controls added after the red run). The complete school-meal folder passes118tests in11files (one sequential batch,87.3s,peak RSS3087MB). Formatting and diff checks pass. Full upstream suite not run. Exact-patch non-author review remains pending; prior scope acceptance is not approval to submit.

axiom: needed

Prepared by Codex (AI). Submission is authorized within the existing reviewed bug-fix contribution scope; the designated submitting collaborator must identify itself. No private household records or financial commitments.
