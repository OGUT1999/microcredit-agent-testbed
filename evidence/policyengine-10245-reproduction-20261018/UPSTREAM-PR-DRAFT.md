Part of #10245 (income eligibility only; territory reimbursement-rate mapping remains open).

Use the contiguous-state income guideline when selecting school-meal tiers for Guam, Puerto Rico and the Virgin Islands. Their generic HHS guideline entries are deliberate zero placeholders, which previously made the school-meal ratio NaN or infinite and selected PAID even below the free/reduced thresholds.

The correction is local to `school_meal_tier`. It leaves `spm_unit_fpg` and the shared `school_meal_fpg_ratio` unchanged, because CSFP and other programs consume them. It does not determine CSFP territory policy or repair reimbursement rates. PR10238's evolving school-meal coverage must be reconciled if it lands first.

Tests cover zero income, both thresholds and the next dollar for one- and two-person units, non-territory controls, and unchanged generic-FPG/CSFP behavior. Test results and non-author review disposition will be filled from the completed validation before submission.

axiom: needed

Prepared by Codex (AI). Submission is authorized within the existing reviewed bug-fix contribution scope; the designated submitting collaborator must identify itself. No private household records or financial commitments.
