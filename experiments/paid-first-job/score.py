#!/usr/bin/env python3
"""Blinded, mechanical scorer for the paid-first-job quotation check (Stage A draft).

  score.py ITEMS_JSON SUBMISSIONS_DIR [--json]

Reads local files only; it contacts nobody and moves no money. SUBMISSIONS_DIR holds
`assignment.json` and one CSV per worker code (`W1.csv` ...). Worker codes are the only
identifiers: names, handles and profiles never enter this directory.

assignment.json:
  {"workers": {"W1": {"set": "A", "deadline": "2026-10-20T12:00Z",
                      "submitted_at": "2026-10-19T09:00Z", "revision_round": 0}, ...}}

CSV columns: item_id, verdict, heard_text, start, end, speaker, note

Optional adjudication.json, written by a person who listened (or read the publisher's own
transcript); agents never write it:
  {"items": {"B05": {"verdict": "MINOR", "heard_text": "...", "basis": "listened"}}}

Payment depends only on what the worker controls and on independent evidence, never on
the other workers: on time; every item answered in the required form; and, for a sheet
with more than a quarter of its items NOT_FOUND, an adjudicator's listening of those items.
Disagreement between workers decides nothing. It only queues items for a human recheck,
and the blog is corrected only from adjudicated items.
"""
import argparse
import csv
import difflib
import hashlib
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone

VERDICTS = ("EXACT", "MINOR", "MAJOR", "NOT_FOUND")
FILLERS = {"uh", "um", "er", "ah", "erm", "hmm"}
TIME_TOLERANCE_S = 60      # a found quotation must start within this of the listed time
MAX_SPAN_S = 120           # one quotation is never longer than this
SIMILAR = 0.85             # transcripts at or above this ratio corroborate each other
NOT_FOUND_HOLD_SHARE = 0.25   # a sheet with more NOT_FOUND than this waits for an adjudicator
FINDS_TO_REVISE = 2           # adjudicator finds this many of a held sheet's NOT_FOUND items: revise
FIELDS = ("item_id", "verdict", "heard_text", "start", "end", "speaker", "note")


def file_sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def parse_time(text):
    """'h:mm:ss', 'm:ss' or 'mm:ss' to seconds; None when malformed."""
    text = (text or "").strip()
    if not re.fullmatch(r"\d{1,2}(:\d{2}){1,2}", text):
        return None
    parts = [int(p) for p in text.split(":")]
    if any(p >= 60 for p in parts[1:]):
        return None
    seconds = 0
    for p in parts:
        seconds = seconds * 60 + p
    return seconds


def parse_utc(text):
    return datetime.strptime(text, "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)


def tokens(text):
    """Lower-case words without punctuation, fillers or immediate repeats ('the the')."""
    text = (text or "").lower().replace("’", "'").replace("‘", "'")
    words = re.findall(r"[a-z0-9]+(?:'[a-z0-9]+)*", text)
    out = []
    for w in words:
        if w in FILLERS or (out and out[-1] == w):
            continue
        out.append(w)
    return out


def similarity(a, b):
    return difflib.SequenceMatcher(None, tokens(a), tokens(b)).ratio()


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_items(path):
    data = load_json(path)
    sets = {}
    for name, spec in data["sets"].items():
        sets[name] = {item["id"]: item for item in spec["items"]}
    return sets


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or tuple(h.strip() for h in reader.fieldnames) != FIELDS:
            return None, ["header must be exactly: " + ",".join(FIELDS)]
        return [{k.strip(): (v or "").strip() for k, v in row.items()} for row in reader], []


def check_rows(rows, items):
    """Per-row form problems and the valid answers by item id."""
    problems, answers = [], {}
    for row in rows:
        iid = row["item_id"]
        if iid not in items:
            problems.append(f"{iid or '(blank)'}: not an item of this set")
            continue
        if iid in answers:
            problems.append(f"{iid}: answered twice")
            continue
        verdict = row["verdict"].upper()
        issues = []
        if verdict not in VERDICTS:
            issues.append("verdict must be one of " + ", ".join(VERDICTS))
        elif verdict == "NOT_FOUND":
            if items[iid].get("at"):
                # Listening at the stated place is required: record what is said there instead.
                start = parse_time(row["start"])
                if not row["heard_text"]:
                    issues.append("NOT_FOUND needs what is said at the listed time in heard_text")
                if start is None or abs(start - parse_time(items[iid]["at"][0])) > TIME_TOLERANCE_S:
                    issues.append("NOT_FOUND needs a start within a minute of the listed time")
            elif not row["note"]:
                issues.append("NOT_FOUND needs a note saying where in the episode you looked")
        else:
            start, end = parse_time(row["start"]), parse_time(row["end"])
            if not row["heard_text"]:
                issues.append("heard_text is empty")
            if not row["speaker"]:
                issues.append("speaker is empty")
            if start is None or end is None:
                issues.append("start and end must be h:mm:ss or m:ss")
            elif end < start or end - start > MAX_SPAN_S:
                issues.append("end must be after start and within two minutes of it")
            else:
                listed = items[iid].get("at")
                if listed and abs(start - parse_time(listed[0])) > TIME_TOLERANCE_S and not row["note"]:
                    issues.append("start is more than a minute from the listed time and note does not explain why")
        if issues:
            problems.extend(f"{iid}: {i}" for i in issues)
        else:
            answers[iid] = dict(row, verdict=verdict)
    for iid in items:
        if iid not in answers and not any(p.startswith(iid + ":") for p in problems):
            problems.append(f"{iid}: not answered")
    return problems, answers


def score(items_path, sub_dir):
    sets = load_items(items_path)
    assignment = load_json(os.path.join(sub_dir, "assignment.json"))["workers"]
    workers = {}
    for code, meta in sorted(assignment.items()):
        items = sets[meta["set"]]
        path = os.path.join(sub_dir, f"{code}.csv")
        if not os.path.exists(path):
            workers[code] = {"set": meta["set"], "submitted": False, "problems": ["no submission"], "answers": {}}
            continue
        rows, header_problems = read_rows(path)
        problems, answers = (header_problems, {}) if rows is None else check_rows(rows, items)
        on_time = "submitted_at" in meta and parse_utc(meta["submitted_at"]) <= parse_utc(meta["deadline"])
        workers[code] = {"set": meta["set"], "submitted": True, "on_time": on_time,
                         "revision_round": int(meta.get("revision_round", 0)),
                         "problems": problems, "answers": answers}

    consensus = {}
    for set_name, items in sets.items():
        members = [c for c, w in workers.items() if w["set"] == set_name]
        for iid, item in items.items():
            given = {c: workers[c]["answers"][iid] for c in members if iid in workers[c]["answers"]}
            counts = Counter(a["verdict"] for a in given.values())
            top = counts.most_common(1)
            majority = top[0][0] if top and top[0][1] >= 2 else None
            consensus[iid] = {"set": set_name, "quoted": item["quoted"], "answers": len(given),
                              "verdicts": dict(counts), "majority": majority}

    adjudicated = {}
    path = os.path.join(sub_dir, "adjudication.json")
    if os.path.exists(path):
        adjudicated = {i: a for i, a in load_json(path).get("items", {}).items() if a.get("verdict") in VERDICTS}

    recheck = set()
    for code, w in workers.items():
        agree = resolved = corroborated = heard = 0
        disputes = []
        for iid, ans in w["answers"].items():
            c = consensus[iid]
            others = [workers[o]["answers"][iid] for o in workers
                      if o != code and workers[o]["set"] == w["set"] and iid in workers[o]["answers"]]
            if c["majority"]:
                resolved += 1
                agree += ans["verdict"] == c["majority"]
            if ans["verdict"] != c["majority"]:
                disputes.append(iid)
            if ans["heard_text"] and any(o["heard_text"] for o in others):
                heard += 1
                corroborated += max(similarity(ans["heard_text"], o["heard_text"]) for o in others) >= SIMILAR
            if ans["verdict"] != "EXACT" or any(o["verdict"] != ans["verdict"] for o in others):
                recheck.add(iid)
        not_found = sorted(i for i, a in w["answers"].items() if a["verdict"] == "NOT_FOUND")
        held = bool(w["answers"]) and len(not_found) > NOT_FOUND_HOLD_SHARE * len(sets[w["set"]])
        w["agreement"] = round(agree / resolved, 3) if resolved else None
        w["corroborated"] = round(corroborated / heard, 3) if heard else None
        w["disputes"] = sorted(disputes)
        w["held_items"] = not_found if held else []
        found_by_adjudicator = [i for i in not_found if adjudicated.get(i, {}).get("verdict") not in (None, "NOT_FOUND")]
        if not w["submitted"]:
            decision = "NO_SUBMISSION"
        elif not w["on_time"]:
            decision = "REJECT_LATE"
        elif w["problems"]:
            decision = "REVISE" if w["revision_round"] == 0 else "REJECT_INCOMPLETE"
        elif held and not all(i in adjudicated for i in not_found):
            decision = "HOLD_ADJUDICATION"
            recheck.update(not_found)
        elif held and len(found_by_adjudicator) >= FINDS_TO_REVISE:
            decision = "REVISE" if w["revision_round"] == 0 else "REJECT_INCOMPLETE"
            w["problems"] = [f"{i}: the adjudicator found it at the stated place" for i in found_by_adjudicator]
        else:
            decision = "ACCEPT"
        w["decision"] = decision
    for w in workers.values():
        w.pop("answers")

    def priority(iid):
        c = consensus[iid]
        return (0 if c["majority"] not in (None, "EXACT") else 1 if c["majority"] is None else 2, iid)

    return {"items_sha256": file_sha256(items_path), "workers": workers, "consensus": consensus,
            "recheck": sorted((i for i in recheck if i not in adjudicated), key=priority),
            "corrections": sorted(i for i, a in adjudicated.items() if a["verdict"] != "EXACT")}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("items")
    ap.add_argument("submissions")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    result = score(args.items, args.submissions)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    print(f"items sha256 {result['items_sha256']}")
    for code, w in result["workers"].items():
        print(f"{code} set {w['set']}: {w['decision']}  agreement {w['agreement']}  corroborated {w['corroborated']}"
              + (f"  held for adjudication {','.join(w['held_items'])}" if w["held_items"] else ""))
        for p in w["problems"]:
            print(f"   - {p}")
    print("items a person must recheck, most likely errors first: " + (", ".join(result["recheck"]) or "none"))
    print("adjudicated corrections for the blog: " + (", ".join(result["corrections"]) or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
