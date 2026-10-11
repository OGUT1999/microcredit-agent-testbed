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

    def adjudicate(self, items):
        with open(os.path.join(self.dir, "adjudication.json"), "w") as f:
            json.dump({"items": items}, f)

    def test_a_correct_minority_is_paid_and_the_split_goes_to_a_person(self):
        # Codex review 6110326408: the published wording is right on two items, W1 says so,
        # W2 and W3 are wrong. Peer disagreement must not cost W1 anything.
        wrong = {"B05": {"verdict": "MINOR", "heard": "as intelligence gets cheap, the coordination gets expensive"},
                 "B08": {"verdict": "MAJOR", "heard": "you're turning a dial into a switch"}}
        self.submit("W1", "B", self.good_rows("B"))
        self.submit("W2", "B", self.good_rows("B", wrong))
        self.submit("W3", "B", self.good_rows("B", wrong))
        result = score.score(ITEMS, self.dir)
        self.assertEqual(result["workers"]["W1"]["decision"], "ACCEPT")
        self.assertEqual(result["workers"]["W1"]["disputes"], ["B05", "B08"])
        self.assertEqual(result["recheck"], ["B05", "B08"])
        self.assertEqual(result["corrections"], [])  # a majority alone corrects nothing
        self.adjudicate({"B05": {"verdict": "EXACT", "basis": "listened"}, "B08": {"verdict": "EXACT", "basis": "listened"}})
        result = score.score(ITEMS, self.dir)
        self.assertEqual(result["recheck"], [])
        self.assertEqual(result["corrections"], [])
        for code in ("W1", "W2", "W3"):
            self.assertEqual(result["workers"][code]["decision"], "ACCEPT")

    def test_blog_corrections_come_only_from_adjudication(self):
        heard = {"B05": {"verdict": "MINOR", "heard": "as intelligence gets cheap, the coordination gets expensive"}}
        for code in ("W1", "W2", "W3"):
            self.submit(code, "B", self.good_rows("B", heard))
        result = score.score(ITEMS, self.dir)
        self.assertEqual((result["recheck"], result["corrections"]), (["B05"], []))
        self.adjudicate({"B05": {"verdict": "MINOR", "basis": "listened"}})
        self.assertEqual(score.score(ITEMS, self.dir)["corrections"], ["B05"])

    def test_recheck_lists_likely_errors_before_splits_and_single_dissents(self):
        self.submit("W1", "B", self.good_rows("B", {"B02": {"verdict": "MINOR"}, "B03": {"verdict": "MAJOR"},
                                                     "B04": {"verdict": "MINOR"}}))
        self.submit("W2", "B", self.good_rows("B", {"B02": {"verdict": "MAJOR"}, "B04": {"verdict": "MINOR"}}))
        self.submit("W3", "B", self.good_rows("B"))
        self.assertEqual(score.score(ITEMS, self.dir)["recheck"], ["B04", "B02", "B03"])

    def test_a_sheet_of_unsupported_not_found_waits_for_a_listener(self):
        nf = {i: {"verdict": "NOT_FOUND", "heard": "", "start": "", "end": "", "note": "searched the whole episode"}
              for i in self.sets["A"]}
        self.submit("W1", "A", self.good_rows("A", nf))
        result = score.score(ITEMS, self.dir)
        self.assertEqual(result["workers"]["W1"]["decision"], "HOLD_ADJUDICATION")
        self.assertEqual(result["workers"]["W1"]["held_items"], sorted(self.sets["A"]))
        found = {i: {"verdict": "EXACT", "basis": "listened"} for i in ("A01", "A02")}
        self.adjudicate({**{i: {"verdict": "NOT_FOUND", "basis": "listened"} for i in self.sets["A"]}, **found})
        result = score.score(ITEMS, self.dir)
        self.assertEqual(result["workers"]["W1"]["decision"], "REVISE")
        self.assertEqual(len(result["workers"]["W1"]["problems"]), 2)
        self.adjudicate({i: {"verdict": "NOT_FOUND", "basis": "listened"} for i in self.sets["A"]})
        self.assertEqual(score.score(ITEMS, self.dir)["workers"]["W1"]["decision"], "ACCEPT")

    def test_not_found_on_a_timed_item_needs_what_was_said_there(self):
        self.submit("W1", "B", self.good_rows("B", {"B08": {"verdict": "NOT_FOUND", "heard": "", "start": "", "end": ""}}))
        problems = score.score(ITEMS, self.dir)["workers"]["W1"]["problems"]
        self.assertTrue(any(p.startswith("B08: NOT_FOUND needs what is said") for p in problems))
        self.assertTrue(any(p.startswith("B08: NOT_FOUND needs a start") for p in problems))
        self.submit("W1", "B", self.good_rows("B", {"B08": {"verdict": "NOT_FOUND", "heard": "so that's the whole debate",
                                                             "start": "55:19", "end": "55:22"}}))
        self.assertEqual(score.score(ITEMS, self.dir)["workers"]["W1"]["decision"], "ACCEPT")

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

    def test_an_untimed_not_found_with_a_note_and_late_or_missing_work(self):
        self.submit("W1", "A", self.good_rows("A", {"A06": {"verdict": "NOT_FOUND", "heard": "", "start": "", "end": "",
                                                             "note": "listened to the whole episode"}}))
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
