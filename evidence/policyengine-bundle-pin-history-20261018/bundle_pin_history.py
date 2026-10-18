#!/usr/bin/env python3
"""Read-only: how often does the `policyengine` bundle move its policyengine-us pin?

Uses only public PyPI JSON metadata. Writes bundle-pin-history.json next to this file
(or to the path given as argv[1]). No installs, no authentication, no writes elsewhere.
"""
import concurrent.futures as cf
import datetime as dt
import json
import statistics
import sys
import urllib.request

UA = {"User-Agent": "claude-steward-readonly/1.0 (AI agent; public metadata read)"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=30))


def releases(project):
    p = get(f"https://pypi.org/pypi/{project}/json")
    rows = []
    for version, files in p["releases"].items():
        if files:
            rows.append((min(f["upload_time_iso_8601"] for f in files), version))
    return sorted(rows)


def us_pin(row):
    uploaded, version = row
    try:
        j = get(f"https://pypi.org/pypi/policyengine/{version}/json")
        pins = [r.split(";")[0].strip() for r in (j["info"].get("requires_dist") or [])
                if r.lower().startswith("policyengine-us")]
        return {"version": version, "uploaded": uploaded, "us_pin": pins[0] if pins else None}
    except Exception as exc:  # keep the row; record the failure
        return {"version": version, "uploaded": uploaded, "us_pin": None, "error": str(exc)[:80]}


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "bundle-pin-history.json"
    bundle = releases("policyengine")
    with cf.ThreadPoolExecutor(8) as ex:
        rows = list(ex.map(us_pin, bundle))
    seq = []
    for r in rows:
        if not seq or seq[-1]["us_pin"] != r["us_pin"]:
            seq.append({"first_version": r["version"], "first_uploaded": r["uploaded"], "us_pin": r["us_pin"]})
    current = seq[-1]
    consecutive = sum(1 for r in rows if r["uploaded"] >= current["first_uploaded"])
    us = releases("policyengine-us")
    us_latest = {"version": us[-1][1], "uploaded": us[-1][0], "total_releases": len(us)}
    held_days = (dt.datetime.now(dt.timezone.utc)
                 - dt.datetime.fromisoformat(current["first_uploaded"].replace("Z", "+00:00"))).days
    intervals = []
    for a, b in zip(seq, seq[1:]):
        da = dt.datetime.fromisoformat(a["first_uploaded"].replace("Z", "+00:00"))
        db = dt.datetime.fromisoformat(b["first_uploaded"].replace("Z", "+00:00"))
        intervals.append((db - da).days)
    result = {
        "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "https://pypi.org/pypi/policyengine/json and per-version JSON; https://pypi.org/pypi/policyengine-us/json",
        "bundle_release_count": len(rows),
        "distinct_us_pin_values_in_sequence": len(seq),
        "current_us_pin": current["us_pin"],
        "current_pin_first_bundle_version": current["first_version"],
        "current_pin_first_uploaded": current["first_uploaded"],
        "bundle_releases_with_current_pin": consecutive,
        "days_current_pin_held_at_generation": held_days,
        "us_latest_on_pypi": us_latest,
        "completed_interval_days_between_pin_changes": {
            "last_five": intervals[-5:], "median_all": statistics.median(intervals)},
        "pin_sequence_last_ten": seq[-10:],
        "rows_with_errors": [r["version"] for r in rows if r.get("error")],
        "releases": rows,
    }
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)
        fh.write("\n")
    keys = ("bundle_release_count", "distinct_us_pin_values_in_sequence", "current_us_pin",
            "current_pin_first_bundle_version", "current_pin_first_uploaded",
            "bundle_releases_with_current_pin", "days_current_pin_held_at_generation", "us_latest_on_pypi")
    print(json.dumps({k: result[k] for k in keys}, indent=2))


if __name__ == "__main__":
    main()
