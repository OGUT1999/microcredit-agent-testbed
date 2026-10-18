#!/usr/bin/env python3
"""Read-only: lag from a human-authored merge to the next 'Update PolicyEngine US' bump commit.

Input on stdin is the output of, run inside a clone of PolicyEngine/policyengine-us:
  git log origin/main --since=2026-09-01 --no-merges --format='%cI|%an|%s'
A bump commit is one authored by the Actions bot; this is a proxy for a release, not proof of one.
"""
import bisect
import datetime as dt
import statistics
import sys

rows = []
for line in sys.stdin:
    if not line.strip():
        continue
    when, author, _subject = line.rstrip("\n").split("|", 2)
    rows.append((dt.datetime.fromisoformat(when).astimezone(dt.timezone.utc), author))
rows.sort()
bots = [t for t, a in rows if a.startswith("Github Actions")]
humans = [t for t, a in rows if not a.startswith("Github Actions")]
lags = []
for h in humans:
    i = bisect.bisect_right(bots, h)
    if i < len(bots):
        lags.append((bots[i] - h).total_seconds() / 3600)
lags.sort()
print("human commits", len(humans), "bot bumps", len(bots))
print("lag hours: median %.2f  p90 %.2f  max %.2f" % (statistics.median(lags), lags[int(0.9 * len(lags))], lags[-1]))
gaps = sorted(((b - a).total_seconds() / 3600, a.isoformat()) for a, b in zip(humans, humans[1:]))[::-1]
print("largest gaps between human commits (hours, start):", [(round(g, 1), s[:16]) for g, s in gaps[:3]])
