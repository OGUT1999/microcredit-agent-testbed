"""Synthetic diagnostic-privacy controls; no real worker or payment records."""
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest

from qualification import MAX_RECORD_BYTES
from quote_consistency import analyze, main
from test_quote_consistency import consistent


class QuoteCLITests(unittest.TestCase):
    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO unavailable on this platform")
    def test_both_clis_reject_fifo_without_waiting_or_private_echo(self):
        with tempfile.TemporaryDirectory(prefix="PRIVATE_SENTINEL_") as directory:
            path = Path(directory) / "record.fifo"
            os.mkfifo(path)
            for name in ("quote_consistency.py", "qualification.py"):
                run = subprocess.run([sys.executable, str(Path(__file__).with_name(name)), str(path)],
                                     capture_output=True, text=True, timeout=2)
                self.assertEqual(run.returncode, 1)
                self.assertEqual(run.stderr, "")
                self.assertNotIn("PRIVATE_SENTINEL", run.stdout)
                self.assertTrue(json.loads(run.stdout)["errors"])

    def cli(self, argv):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            rc = main(argv)
        self.assertEqual(stderr.getvalue(), "")
        self.assertNotIn("PRIVATE_SENTINEL", stdout.getvalue())
        result = json.loads(stdout.getvalue())
        self.assertFalse(result["channel_pass"])
        self.assertFalse(result["human_earnings_established"])
        return rc, result

    def test_valid_cli_omits_labels_preserves_exact_bounds_and_api(self):
        data = consistent()
        for index, quote in enumerate(data["quotes"]):
            quote["id"] = "PRIVATE_SENTINEL_" + str(index)
            quote["currency"] = "PRIVATE_SENTINEL_UNIT"
        expected = analyze(data)
        with tempfile.TemporaryDirectory(prefix="PRIVATE_SENTINEL_") as directory:
            path = Path(directory) / "record.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            rc, result = self.cli([str(path)])
        self.assertEqual(rc, 0)
        self.assertEqual(result["status"], "QUOTE_ARITHMETIC_CONSISTENT")
        self.assertEqual(result["rate_intervals"], [
            {"interval_index": i, "low_cash_per_point": q["low_cash_per_point"],
             "high_cash_per_point": q["high_cash_per_point"]}
            for i, q in enumerate(expected["rate_intervals"])])
        self.assertEqual(expected["rate_intervals"][0]["id"], "PRIVATE_SENTINEL_0")

    def test_invalid_cli_discards_partial_intervals_and_bad_values(self):
        data = consistent()
        data["quotes"][0]["id"] = "PRIVATE_SENTINEL"
        data["quotes"][1]["points_min"] = "PRIVATE_SENTINEL"
        with tempfile.TemporaryDirectory(prefix="PRIVATE_SENTINEL_") as directory:
            path = Path(directory) / "record.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            rc, result = self.cli([str(path)])
        self.assertEqual((rc, result["status"]), (1, "INVALID_QUOTE"))
        self.assertEqual(result["rate_intervals"], [])

    def test_read_parse_encoding_size_depth_and_integer_failures_private(self):
        with tempfile.TemporaryDirectory(prefix="PRIVATE_SENTINEL_") as directory:
            path = Path(directory) / "record.json"
            for raw in (b'PRIVATE_SENTINEL', b'\xffPRIVATE_SENTINEL',
                        b'[' * 10000 + b']' * 10000,
                        b' ' * (MAX_RECORD_BYTES + 1), b'1' * 10000):
                path.write_bytes(raw)
                rc, result = self.cli([str(path)])
                self.assertEqual((rc, result["status"]), (1, "INVALID_QUOTE"))
                self.assertEqual(result["rate_intervals"], [])
            for target in (str(Path(directory) / "missing.json"), directory,
                           "PRIVATE_SENTINEL\x00"):
                rc, result = self.cli([target])
                self.assertEqual((rc, result["status"]), (1, "INVALID_QUOTE"))

    def test_duplicate_members_at_any_depth_reject_even_unused(self):
        data = json.dumps(consistent())
        cases = [data[:-1] + ',"quotes":[]}',
                 data.replace('"points_min": "1000"',
                              '"points_min":"PRIVATE_SENTINEL","points_min":"1000"'),
                 data[:-1] + ',"unused":{"PRIVATE_SENTINEL":1,"PRIVATE_SENTINEL":2}}']
        with tempfile.TemporaryDirectory(prefix="PRIVATE_SENTINEL_") as directory:
            path = Path(directory) / "record.json"
            for raw in cases:
                path.write_text(raw, encoding="utf-8")
                rc, result = self.cli([str(path)])
                self.assertEqual((rc, result["status"]), (1, "INVALID_QUOTE"))

    def test_nonstandard_literals_reject_even_unused(self):
        with tempfile.TemporaryDirectory(prefix="PRIVATE_SENTINEL_") as directory:
            path = Path(directory) / "record.json"
            for literal in ("NaN", "Infinity", "-Infinity"):
                path.write_text(json.dumps(consistent())[:-1] + ',"unused":' + literal + '}',
                                encoding="utf-8")
                rc, result = self.cli([str(path)])
                self.assertEqual((rc, result["status"]), (1, "INVALID_QUOTE"))

    def test_argument_errors_private(self):
        for argv in ([], ["--PRIVATE_SENTINEL"], ["record.json", "PRIVATE_SENTINEL"]):
            rc, result = self.cli(argv)
            self.assertEqual((rc, result["status"]), (1, "INVALID_QUOTE"))

    def test_historical_fixture_preserves_status_and_exact_arithmetic(self):
        path = Path(__file__).with_name("fieldwork-quote-regression-2026-10-13.json")
        rc, result = self.cli([str(path)])
        expected = analyze(json.loads(path.read_text()))
        self.assertEqual((rc, result["status"]), (1, "INCOMPLETE_QUOTE"))
        self.assertFalse(result["fixed_rate_compatible"])
        self.assertEqual([q["low_cash_per_point"] for q in result["rate_intervals"]],
                         [q["low_cash_per_point"] for q in expected["rate_intervals"]])

    def test_scalar_and_malformed_shapes_reject_privately(self):
        with tempfile.TemporaryDirectory(prefix="PRIVATE_SENTINEL_") as directory:
            path = Path(directory) / "record.json"
            for data in (None, "PRIVATE_SENTINEL", [], {}, {"quotes": [None, None]}):
                path.write_text(json.dumps(data), encoding="utf-8")
                rc, result = self.cli([str(path)])
                self.assertEqual((rc, result["status"]), (1, "INVALID_QUOTE"))

    def test_unit_mismatch_still_incomplete_after_redaction(self):
        data = consistent()
        data["quotes"][0]["currency"] = "PRIVATE_SENTINEL"
        with tempfile.TemporaryDirectory(prefix="PRIVATE_SENTINEL_") as directory:
            path = Path(directory) / "record.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            rc, result = self.cli([str(path)])
        self.assertEqual((rc, result["status"]), (1, "INCOMPLETE_QUOTE"))
        self.assertFalse(result["currency_confirmed"])
        self.assertIsNone(result["fixed_rate_compatible"])

    def test_exact_size_boundary_accepts_and_next_byte_rejects(self):
        raw = json.dumps(consistent()).encode("utf-8")
        with tempfile.TemporaryDirectory(prefix="PRIVATE_SENTINEL_") as directory:
            path = Path(directory) / "record.json"
            path.write_bytes(raw + b' ' * (MAX_RECORD_BYTES - len(raw)))
            rc, result = self.cli([str(path)])
            self.assertEqual(rc, 0)
            path.write_bytes(raw + b' ' * (MAX_RECORD_BYTES + 1 - len(raw)))
            rc, result = self.cli([str(path)])
            self.assertEqual((rc, result["status"]), (1, "INVALID_QUOTE"))

    def test_help_keeps_normal_exit(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr), self.assertRaises(SystemExit) as caught:
            main(["--help"])
        self.assertEqual(caught.exception.code, 0)
        self.assertEqual(stderr.getvalue(), "")
        self.assertIn("quote_consistency.py", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
