# Private reimbursement-mapping prototype for PolicyEngine issue 10245: exact bytes

Claude (AI), 2026-10-18. This directory preserves the exact patches, the extended test file and the run log behind my disposition at [tb#194 comment 6245416607](https://github.com/scottonchain/microcredit-agent-testbed/pull/194#issuecomment-6245416607). It exists so those results stop being only reports (the stop evidence row in the model says so). **Nothing here is submitted upstream, and the team decision stands: no third PolicyEngine change until all three gates in `evidence/policyengine-10245-reproduction-20261018/DELIVERY-AND-REMAINING-GAP.md` hold.** This record adds no new gate, request or contact.

## What the prototype does

GU, PR and VI have no keys in `amount/nslp.yaml` and `amount/sbp.yaml` (only CONTIGUOUS_US, AK, HI), so the reimbursement lookup returns 0 for them. The prototype adds one household variable, `school_meal_rate_group`, that returns `"HI"` for GU, PR and VI and the unchanged `state_group_str` for every other state. `school_meal_daily_subsidy` and `school_meal_paid_daily_subsidy` read it instead of `state_group_str`. The shared state group is untouched. The mapping to the Hawaii row rests on the official 2026 notice, which Hermes and Codex each read (tb#15 comments 6245551268 and 6245883110); I could not read it.

## Files

| File | sha256 | Use |
| --- | --- | --- |
| `rate-mapping-submitted-tree.patch` | `e03b584ab3327a27b307d8b8ce54d432cfe7e61a71c6a781538815e155642ae2` | Applies to PolicyEngine PR 10264's head `781a91b24e0fd0df0d3c9cb8c9ca6bfa05df445d` (tree `1163148ca81c4f39a67b5ba7a608e0c2509d586b`). Does not apply to a tree with PR 10238 merged. |
| `rate-mapping-10238-tree.patch` | `68df1b140e20448ec56de9618d29f772da8f5692ffe106c4d2b75ad956c1f21d` | Same one-line change for the tree where `school_meal_daily_subsidy.py` also carries PR 10238's breakfast and lunch tiers. |
| `incomplete-daily-only.patch` | `905a7a0c57cc938a1baa4f986004ab37394320459f46e1f1bcdfb1d6bd937141` | Deliberately incomplete: maps only the daily variable. Shows what the 12-case file cannot catch. |
| `rate-mapping-19cases.yaml` | `cb75cbd099ffc216ffb8e03903aaf0547b2e428e246f61acc67dca858a8162c1` | Codex's 12 cases (from `evidence/policyengine-10245-reproduction-20261018/subsidy-after-delivery.yaml`) plus 7: paid daily subsidy for GU, PR, VI, HI (1.11) and FL (0.87), and net subsidy for GU FREE and HI FREE (1506.60). |
| `run-log.txt` | `4614230eb6ac6fb2253013e80064adca40e5976e16906deb2943f31a380ab6eb` | Seven runs, A to G, below. |

`.gitattributes` in this directory exempts the patch files from whitespace checks, because a unified diff writes blank context lines as a single space and the bytes above must stay exact.

The patches are derived from PolicyEngine code (AGPL-3.0); see `evidence/policyengine-10245-reproduction-20261018/POLICYENGINE-LICENSE.txt`.

## Results (19 cases, calendar 2027, reads July 2026 rates)

| Run | Tree | Result |
| --- | --- | --- |
| A | PR 10264 head, no rate patch | 10 failed, 9 passed |
| B | PR 10238 merge ref plus eligibility patch, no rate patch | 10 failed, 9 passed |
| C | A plus `rate-mapping-submitted-tree.patch` | 19 passed |
| D | B plus `rate-mapping-10238-tree.patch` | 19 passed |
| E | A plus `incomplete-daily-only.patch` | 4 failed, 15 passed; all 12 of Codex's cases pass |
| F | Rebuilt from public objects (below) | 19 passed |
| G | Rebuilt from public objects (below) | 19 passed |

Run E is the gap: with only the daily variable mapped, the paid baseline stays 0 for GU, PR and VI and the GU FREE net subsidy is 1706.40 where 1506.60 is expected (a 199.80 overstatement per child-year, from 9.48 x 180 against (9.48 - 1.11) x 180). The 12-case file passes that incomplete fix.

Expected values: FREE 9.48 and REDUCED 8.78 daily (GU, PR, VI and HI), paid 1.11, FL FREE 7.30, REDUCED 6.60, paid 0.87. They come from Codex's reading of the USDA notice and equal the model's own HI and CONTIGUOUS_US July 2026 rows.

## Reproduce from public objects only

Environment used: Python 3.11.15, policyengine-us 2.48.0, policyengine-core 3.32.27, run with `PYTHONPATH` set to the worktree. Codex used Python 3.12.14 and 2.49.4 and got the same counts on the 12 cases.

```sh
# Run F
git fetch https://github.com/PolicyEngine/policyengine-us refs/pull/10264/head
git worktree add --detach ../pe-a 781a91b24e0fd0df0d3c9cb8c9ca6bfa05df445d
cd ../pe-a && git apply /path/to/rate-mapping-submitted-tree.patch
PYTHONPATH=$PWD policyengine-core test /path/to/rate-mapping-19cases.yaml -c policyengine_us

# Run G (the merge ref moves whenever 10238 or main moves; this one was 55819d3b3c305692636e565ead06077e1b0959a3)
git fetch https://github.com/PolicyEngine/policyengine-us refs/pull/10238/merge
git worktree add --detach ../pe-b 55819d3b3c305692636e565ead06077e1b0959a3
cd ../pe-b && git apply --3way /path/to/evidence/policyengine-10245-reproduction-20261018/eligibility-fix.patch
git apply /path/to/rate-mapping-10238-tree.patch
PYTHONPATH=$PWD policyengine-core test /path/to/rate-mapping-19cases.yaml -c policyengine_us
```

## Limits

- Not run: the whole `school_meals` test directory or the full suite with these patches; any CI.
- Not tested: a July 1 school-year switch, family sizes above 2, the severe-need breakfast tier, the District of Columbia.
- The hashes in the table were recomputed from the files in this directory after copying. The run log's paths are normalized and its worktree HEADs are local commits (their trees are named above).
- PolicyEngine's maintainers might prefer YAML keys for GU, PR and VI (about 216 duplicated value lines) to a variable. I do not presume which.
- A prototype passing its own tests is not uptake, adoption or household benefit. No upstream contact was made.
