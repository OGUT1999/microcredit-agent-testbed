# How fast does a PolicyEngine US fix reach the public calculator path? Bundle pin history

Claude (AI), 2026-10-18. Read-only provenance check for the Florida tips fix (PolicyEngine PR 10263), done while answering [tb#17 comment 6248934238](https://github.com/scottonchain/microcredit-agent-testbed/issues/17#issuecomment-6248934238) and reviewing draft PR 199. Public metadata only: PyPI JSON, `git log` of public repositories. No package was installed or run, no account used, no one contacted.

## Question

If PR 10263 merges, how soon does the corrected calculation reach the one consumer path PR 199 identified (the PolicyEngine API, which pins the `policyengine` bundle, which pins one `policyengine-us` version)?

## Results (generated 2026-10-18 about 10:50Z)

| Link | Observation | Source |
| --- | --- | --- |
| Merge to version bump | Median 0.75 hours, 90th percentile 8.72, maximum 57.14, over 562 human-authored commits since 2026-09-01 and 257 bot bump commits. A bump commit is a proxy for a release. | `merge_to_bump_lag.py` on `git log` of `policyengine-us`; output in `merge-to-bump-lag-output.txt` |
| Bump to PyPI upload | 0.65 hours for 2.2.1 (bump 2026-09-15T04:06:42Z, wheel 04:45:46Z); 1.54 hours for 2.49.4 (bump 2026-10-16T20:00:39Z, wheel 21:33:06Z). Two samples. | git commit times, PyPI JSON |
| Bundle's US pin | 171 bundle releases; the pin takes 23 distinct values in sequence. Current pin `policyengine-us==2.2.1` since bundle 6.0.0 (2026-09-15T13:37Z): 27 consecutive releases (6.0.0 to 6.7.3), 32 days at generation. US itself is at 2.49.4 (206 US releases). | `bundle_pin_history.py`; `bundle-pin-history.json` |
| Intervals between pin changes | Last five completed intervals, in days: 10, 4, 1, 7, 68. Median over all history: 2.5 days. The current pin has held 32 days and counting. | `bundle-pin-history.json` |
| Defect inside the pinned build | `tip_income` is in `policyengine_us/parameters/gov/states/fl/doe/sr/income/sources.yaml` at commit `f88982f25e` (the 2.2.1 bump, 2026-09-15) and on main `5ec60b2`. | `git show` on a clone of `policyengine-us` |
| API pin | `PolicyEngine/policyengine-api` `master` is `71dba65` (2026-10-16T06:55:31Z); `pyproject.toml` pins `policyengine[models]==6.5.0`; `uv.lock` resolves `policyengine-us` 2.2.1. The latest bundle on PyPI is 6.7.3. | `git show` on a depth-1 fetch |

## Reading, and what it does not show

- A merged fix reaches pip users of `policyengine-us` within roughly one to three hours. It reaches the API path only after the bundle certifies a newer US version. The bundle repository's `docs/release-bundles.md` describes the model pin as set by a certification step derived from a country data-release manifest.
- **The history is not uniformly slow.** Over all history the median interval between pin changes is 2.5 days; the pin moved every few days through spring and early summer. The two most recent intervals (68 days, then 32 days and counting) mark a slower regime that began after 2026-07-09 and includes the US 1.x to 2.x transition. A recertification could come tomorrow or not for weeks; this record does not predict it.
- It does not show whether production runs API commit `71dba65`, whether other consumers matter more, or any actual use. Those links are unknown.
- Experiment scoring suggestion (not a decision): count merge and PyPI release (hours) inside the response window; treat bundle pin, deployment and use as later events, not as failure when absent within the window.

## Reproduce

```sh
# bundle pin history (PyPI only)
python3 bundle_pin_history.py bundle-pin-history.json

# merge to bump lag (inside a clone of PolicyEngine/policyengine-us, history since 2026-09-01)
git log origin/main --since=2026-09-01 --no-merges --format='%cI|%an|%s' | python3 merge_to_bump_lag.py

# defect inside the 2.2.1 build
git show f88982f25e:policyengine_us/parameters/gov/states/fl/doe/sr/income/sources.yaml | grep tip_income

# API pin
git init x && cd x && git fetch --depth=1 https://github.com/PolicyEngine/policyengine-api HEAD
git show FETCH_HEAD:pyproject.toml | grep 'policyengine\[models\]'
git show FETCH_HEAD:uv.lock | grep -A1 'name = "policyengine-us"'
```

## Limits

- Counts are as of generation time and will move; `bundle-pin-history.json` carries the generation time.
- A "bump commit" is a release proxy. The git history I could read starts at 2026-09-01 (a shallow clone).
- PyPI upload time is the earliest file time for a release.
- I could not reach the Federal Register, Olas, the ERC-8183 page or the Florida program page from my session; nothing here depends on them.
- This record is an internal learning artifact, not external uptake and not evidence of human benefit.
