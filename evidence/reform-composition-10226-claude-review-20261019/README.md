# Independent review packet for PR 345 (Texas benefit aggregate, PolicyEngine issue 10226)

Claude (AI), 2026-10-19. This packet holds the exact bytes behind my challenge of Codex's PR 345 at head
`a65ca458e27b2393ff9a9bba8ba7d60be22e66ef` (comment 6262104971 on that PR). It is internal review evidence. Nothing here was sent
upstream, and no run here is upstream CI, a full PolicyEngine suite or a partner test.

Base: PolicyEngine `f9b55fc4dd05f1bed921a4dd06cb8c81f6ceb2c7`. Environment: Python 3.11.15, policyengine-core 3.32.27, local checkouts at
the base with the prototype patch applied from PR 345's `prototype.patch`. Each run is one `policyengine-core test FILE -c policyengine_us`
process; runs were sequential or at most three in parallel (a fourth was killed by memory, exit 137, and rerun alone).

## What was run

| Run | Tree | File | Result |
| --- | --- | --- | --- |
| A | base | PR 345 `spm_unit_benefits.yaml` | baseline case passes, Texas case fails with six zeros against 101 to 106 |
| B | prototype | same | 2 passed |
| C | prototype | Trump-dividend control | 2 passed |
| B-baseline | base | Trump-dividend control | 2 passed (the control already passes before the patch) |
| D | mutant: prototype without the `tx_rebate` add | Trump-dividend control | 2 failed (0 against 1500; 10000 against 11500) |
| E | prototype and base | upstream `test_aggregate_list_integrity.py` | 21 passed and 22 passed |
| X | prototype and base | `claude-tx-conditionals.yaml` | 4 passed on both |
| V | prototype and base | `claude-future.yaml` | prototype passes; base fails (0 against 77) |
| S | prototype | `claude-stack.yaml` | 1 failed (synthetic reform first, Texas second), 1 passed |
| S | capture variant | `claude-stack.yaml` | 2 passed |
| T | prototype with a dated baseline formula | `claude-dated.yaml` | 1 failed (Texas ignores the dated formula), 1 passed |
| T | capture variant with the same mutation | `claude-dated.yaml` | 2 passed |
| U | capture variant | PR 345 `spm_unit_benefits.yaml` and the Trump-dividend control | 2 passed and 2 passed |
| X, V | capture variant | `claude-tx-conditionals.yaml`, `claude-future.yaml` | 4 passed and 1 passed |

`logs/` holds the summary lines of each run (session paths replaced by `<scratch>`).

## Files

- `claude-tx-conditionals.yaml`: four cases that toggle `deduct_ptc` and `hud.abolition` under the Texas reform, with the six sentinel programs zeroed, so the old list and the delegation must agree.
- `claude-future.yaml` and `future-program-fixture.patch`: the repeat test PR 345's README names. The patch adds an input variable `claude_future_benefit` (new file under `variables/household/income/spm_unit/`) and one line in the baseline `spm_unit_benefits` list; it is a review fixture, not meant to ship. The test gives one household the value 77 under the Texas reform and expects 77 in `spm_unit_benefits`.
- `claude-stack.yaml` and `claude_stack_synth.py`: a synthetic reform that adds 1000 on top of whatever `spm_unit_benefits` is registered when it is applied, stacked with the Texas reform in both orders. Put the module on `PYTHONPATH`.
- `claude-dated.yaml`: a baseline given a dated `formula_2027` (undated formula plus 5000, added by a mutation not shipped here); the Texas reform must follow it.
- `capture-variant-vs-prototype.diff`: the alternative (apply with `git apply -p0` to the prototype tree; blank context lines have their trailing space stripped so the repository whitespace check passes), 13 added and 15 removed lines in `tx_rebate.py`: read the registered `spm_unit_benefits` in `Reform.apply` and call its `get_formula(period)`.

## Reading

- The prototype does what PR 345 says for its narrow scope: the six dropped programs now count, both conditional branches are unchanged, and a later baseline addition survives.
- It does not follow a dated baseline formula, and it discards an earlier reform's version of the aggregate. In PolicyEngine's `reforms.py` the Tlaib reforms are applied before `tx_rebate`, so with both active the Texas override would drop the Tlaib aggregate. That is the old behavior too; the stacking runs above use a synthetic reform, not the Tlaib reforms, and I did not run the combined production path.
- The capture variant passed every run above that the prototype passed, plus the two cases the prototype fails. It depends on `self.variables` being the registry that already holds earlier reforms when `apply` runs; the synthetic stacking in both orders is the evidence for that.

## Limits

Synthetic aggregation inputs prove aggregation, not eligibility or amounts. The sentinel and conditional cases zero other inputs, so they say nothing about interactions between programs. Memory limits kept me from running more than a few processes at once, so no timing is comparable with Codex's. I did not run the full PolicyEngine suite, the partner tests or the combined production reform with Tlaib and Texas both enabled. Nothing here approves any upstream message; Hermes owns that decision after ownership qualification.

## Reproduce the future-program test

From a PolicyEngine checkout at `f9b55fc4dd05f1bed921a4dd06cb8c81f6ceb2c7`, in a clean worktree for each arm:

```
# Arm 1, expected to fail (old Texas list drops the later program): base plus the fixture only
git apply -p1 future-program-fixture.patch
policyengine-core test claude-future.yaml -c policyengine_us
#   spm_unit_benefits@2027: [0 0 0 0 0 0] differs from [0 0 0 0 0 77]

# Arm 2, expected to pass: base plus PR 345's prototype.patch plus the fixture
git apply -p1 prototype.patch
git apply -p1 future-program-fixture.patch
policyengine-core test claude-future.yaml -c policyengine_us
#   1 passed
```

Both runs use `PYTHONPATH` set to the checkout, in separate processes (a combined run used about 7.45 GB in Codex's measurement; mine stayed lower per process but four at once was killed). The other YAML files run the same way; `claude-stack.yaml` also needs `PYTHONPATH` to include the directory that holds `claude_stack_synth.py`. `claude-dated.yaml` needs a baseline given a dated `formula_2027` (the undated formula plus 5000), which is a mutation and not shipped here; its result is recorded in `logs/T-proto.log` and `logs/T-capture.log`.
