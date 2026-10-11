import contextlib
import csv
import io
import json
import os
import tempfile
import unittest

import score

HERE = os.path.dirname(os.path.abspath(__file__))
ITEMS = os.path.join(HERE, "items.json")
# Frozen before recruitment: a changed item file is a new task and needs a new cost card.
ITEMS_SHA256 = "9325412d2226dee20201122b455f3501c50e5f2ea59208c2c427899eb0819f19"


def row(item_id, verdict="EXACT", heard="", start="1:00", end="1:05", speaker="S", note=""):
    return {"item_id": item_id, "verdict": verdict, "heard_text": heard, "start": start, "end": end,
            "speaker": speaker, "note": note}


class ScoreTest(unittest.TestCase):
    def setUp(self):
        self.sets = score.load_items(ITEMS)
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = tmp.name
        self.assignment = {}

    def submit(self, code, set_name, rows, submitted_at="2026-10-20T09:00Z", deadline="2026-10-20T12:00Z",
               revision_round=0, header=score.FIELDS):
        self.assignment[code] = {"set": set_name, "deadline": deadline, "submitted_at": submitted_at,
                                 "revision_round": revision_round}
        with open(os.path.join(self.dir, f"{code}.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=header)
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, "") for k in header})
        self.write_assignment()

    def write_assignment(self):
        with open(os.path.join(self.dir, "assignment.json"), "w") as f:
            json.dump({"workers": self.assignment}, f)

    def good_rows(self, set_name, overrides=None):
        rows = []
        for iid, item in self.sets[set_name].items():
            at = item.get("at")
            start = at[0] if at else "1:00"
            r = row(iid, heard=item["quoted"], start=start, end=start, speaker=item["speaker"])
            r.update({("heard_text" if k == "heard" else k): v for k, v in (overrides or {}).get(iid, {}).items()})
            rows.append(r)
        return rows

    def test_item_file_is_frozen_and_well_formed(self):
        self.assertEqual(score.file_sha256(ITEMS), ITEMS_SHA256)
        ids = [i for s in self.sets.values() for i in s]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual({k: len(v) for k, v in self.sets.items()}, {"A": 9, "B": 11})
        for s in self.sets.values():
            for item in s.values():
                if item["at"]:
                    self.assertIsNotNone(score.parse_time(item["at"][0]))

    def test_time_parsing(self):
        self.assertEqual(score.parse_time("2:33:47"), 9227)
        self.assertEqual(score.parse_time("15:19"), 919)
        for bad in ("", "15", "1:75", "a:bc", "1:2"):
            self.assertIsNone(score.parse_time(bad), bad)

    def test_tokens_ignore_fillers_repeats_and_punctuation(self):
        self.assertEqual(score.tokens("I do feel myself as kind of the the birdie"),
                         score.tokens("I, uh, do feel myself as kind of the birdie."))
        self.assertEqual(score.tokens("It’s just"), ["it's", "just"])

    def test_three_honest_workers_are_all_accepted(self):
        for code in ("W1", "W2", "W3"):
            self.submit(code, "B", self.good_rows("B"))
        result = score.score(ITEMS, self.dir)
        for code in ("W1", "W2", "W3"):
            self.assertEqual(result["workers"][code]["decision"], "ACCEPT")
            self.assertEqual(result["workers"][code]["agreement"], 1.0)
        self.assertEqual(result["corrections"], [])

    def test_majority_finds_a_caption_error_and_a_minority_is_not_penalised(self):
        heard = {"B05": {"verdict": "MINOR", "heard": "as intelligence gets cheap, the coordination gets expensive"}}
        self.submit("W1", "B", self.good_rows("B", heard))
        self.submit("W2", "B", self.good_rows("B", heard))
        self.submit("W3", "B", self.good_rows("B"))  # reports the published wording once: one flag only
        result = score.score(ITEMS, self.dir)
        self.assertEqual(result["consensus"]["B05"]["majority"], "MINOR")
        self.assertEqual(result["corrections"], ["B05"])
        self.assertEqual(result["workers"]["W3"]["copy_flags"], ["B05"])
        self.assertEqual(result["workers"]["W3"]["decision"], "ACCEPT")
        self.assertLess(result["workers"]["W3"]["agreement"], 1.0)

    def test_published_wording_against_two_listeners_twice_is_rejected(self):
        heard = {"B05": {"verdict": "MINOR", "heard": "as intelligence gets cheap, the coordination gets expensive"},
                 "B08": {"verdict": "MAJOR", "heard": "you're turning a dial into a switch"}}
        self.submit("W1", "B", self.good_rows("B", heard))
        self.submit("W2", "B", self.good_rows("B", heard))
        self.submit("W3", "B", self.good_rows("B"))
        result = score.score(ITEMS, self.dir)
        self.assertEqual(result["workers"]["W3"]["decision"], "REJECT_UNHEARD")
        self.assertEqual(sorted(result["corrections"]), ["B05", "B08"])

    def test_incomplete_work_gets_one_revision_then_rejection(self):
        rows = self.good_rows("A")[:-1]
        self.submit("W4", "A", rows)
        result = score.score(ITEMS, self.dir)
        self.assertEqual(result["workers"]["W4"]["decision"], "REVISE")
        self.assertIn("A09: not answered", result["workers"]["W4"]["problems"])
        self.submit("W4", "A", rows, revision_round=1)
        self.assertEqual(score.score(ITEMS, self.dir)["workers"]["W4"]["decision"], "REJECT_INCOMPLETE")

    def test_form_problems_are_named(self):
        rows = self.good_rows("B", {"B01": {"verdict": "maybe"}, "B02": {"start": "15:47", "end": "19:00"},
                                    "B03": {"heard": ""}, "B04": {"start": "2:40:00", "end": "2:40:05"}})
        rows.append(row("A01"))
        self.submit("W5", "B", rows)
        problems = score.score(ITEMS, self.dir)["workers"]["W5"]["problems"]
        self.assertTrue(any(p.startswith("B01: verdict") for p in problems))
        self.assertTrue(any(p.startswith("B02: end") for p in problems))
        self.assertTrue(any(p.startswith("B03: heard_text") for p in problems))
        self.assertTrue(any(p.startswith("B04: start is more than a minute") for p in problems))
        self.assertTrue(any(p.startswith("A01: not an item") for p in problems))

    def test_a_far_timestamp_with_an_explanation_is_accepted(self):
        self.submit("W5", "B", self.good_rows("B", {"B04": {"start": "2:40:00", "end": "2:40:05",
                                                             "note": "said again later; the listed time is the first take"}}))
        self.assertEqual(score.score(ITEMS, self.dir)["workers"]["W5"]["decision"], "ACCEPT")

    def test_not_found_needs_no_text_and_late_or_missing_work_is_not_accepted(self):
        self.submit("W1", "A", self.good_rows("A", {"A06": {"verdict": "NOT_FOUND", "heard": "", "start": "", "end": ""}}))
        self.submit("W2", "A", self.good_rows("A"), submitted_at="2026-10-21T09:00Z")
        self.assignment["W3"] = {"set": "A", "deadline": "2026-10-20T12:00Z"}
        self.write_assignment()
        result = score.score(ITEMS, self.dir)
        self.assertEqual(result["workers"]["W1"]["decision"], "ACCEPT")
        self.assertEqual(result["workers"]["W2"]["decision"], "REJECT_LATE")
        self.assertEqual(result["workers"]["W3"]["decision"], "NO_SUBMISSION")

    def test_wrong_header_is_a_named_problem(self):
        self.submit("W6", "A", [], header=("id", "verdict"))
        result = score.score(ITEMS, self.dir)
        self.assertEqual(result["workers"]["W6"]["decision"], "REVISE")
        self.assertTrue(result["workers"]["W6"]["problems"][0].startswith("header must be"))

    def test_cli_prints_decisions(self):
        self.submit("W1", "A", self.good_rows("A"))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(score.main([ITEMS, self.dir]), 0)
        self.assertIn("W1 set A: ACCEPT", out.getvalue())


if __name__ == "__main__":
    unittest.main()
