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

The decision uses only what a worker controls: on time, every item answered in the
required form, and no published wording reported as heard where the two other workers
on the set heard something else. Agreement with the other workers is reported as a
quality measure but never decides payment, so a worker who is right against a mistaken
majority is not penalised.
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
COPY_FLAGS_TO_REJECT = 2   # published wording reported as heard against a two-worker majority
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
        elif verdict != "NOT_FOUND":
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

    for code, w in workers.items():
        agree = resolved = corroborated = heard = 0
        copy_flags = []
        for iid, ans in w["answers"].items():
            c = consensus[iid]
            others = [workers[o]["answers"][iid] for o in workers
                      if o != code and workers[o]["set"] == w["set"] and iid in workers[o]["answers"]]
            other_verdicts = Counter(o["verdict"] for o in others)
            if c["majority"]:
                resolved += 1
                agree += ans["verdict"] == c["majority"]
            if ans["heard_text"] and any(o["heard_text"] for o in others):
                heard += 1
                corroborated += max(similarity(ans["heard_text"], o["heard_text"]) for o in others) >= SIMILAR
            # Published wording reported as heard, while both other workers heard something else.
            same_as_published = tokens(ans["heard_text"]) == tokens(c["quoted"])
            differs = sum(n for v, n in other_verdicts.items() if v != "EXACT")
            if ans["heard_text"] and same_as_published and differs >= 2:
                copy_flags.append(iid)
        w["agreement"] = round(agree / resolved, 3) if resolved else None
        w["corroborated"] = round(corroborated / heard, 3) if heard else None
        w["copy_flags"] = copy_flags
        if not w["submitted"]:
            decision = "NO_SUBMISSION"
        elif not w["on_time"]:
            decision = "REJECT_LATE"
        elif len(copy_flags) >= COPY_FLAGS_TO_REJECT:
            decision = "REJECT_UNHEARD"
        elif w["problems"]:
            decision = "REVISE" if w["revision_round"] == 0 else "REJECT_INCOMPLETE"
        else:
            decision = "ACCEPT"
        w["decision"] = decision
    for w in workers.values():
        w.pop("answers")

    return {"items_sha256": file_sha256(items_path), "workers": workers, "consensus": consensus,
            "corrections": sorted(i for i, c in consensus.items() if c["majority"] in ("MINOR", "MAJOR", "NOT_FOUND"))}


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
              + (f"  copy flags {','.join(w['copy_flags'])}" if w["copy_flags"] else ""))
        for p in w["problems"]:
            print(f"   - {p}")
    print("items the majority says the blog must correct: " + (", ".join(result["corrections"]) or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
