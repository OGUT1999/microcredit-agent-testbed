"""Synthetic CLI privacy controls, never observed worker or poverty outcomes."""
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from human_outcome_gate import classify, main, UNKNOWN
from scripts.record_input import MAX_RECORD_BYTES, read_record
from test_human_outcome_gate import packet

ROOT = Path(__file__).resolve().parents[1]


class OutcomeCLITests(unittest.TestCase):
    def cli(self, argv):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            rc = main(argv)
        self.assertEqual(stderr.getvalue(), "")
        self.assertNotIn("PRIVATE_SENTINEL", stdout.getvalue())
        result = json.loads(stdout.getvalue())
        for flag in ("human_earnings_established", "poverty_reduction_established", "financial_authority"):
            self.assertIs(result[flag], False)
        return rc, result

    def from_data(self, data):
        with tempfile.TemporaryDirectory(prefix="PRIVATE_SENTINEL_") as directory:
            path = Path(directory) / "packet.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            return self.cli([str(path)])

    def test_success_omits_labels_preserves_all_readiness_gaps_and_numeric_results(self):
        data = json.loads(json.dumps(packet()).replace("synthetic", "PRIVATE_SENTINEL")
                          .replace('"NLE"', '"PRIVATE_SENTINEL_UNIT"'))
        before = deepcopy(data)
        expected = classify(data)
        rc, actual = self.from_data(data)
        self.assertEqual(rc, 0)
        self.assertEqual(data, before)
        self.assertEqual(expected["reported_earnings_arithmetic"]["currency"], "PRIVATE_SENTINEL_UNIT")
        del expected["reported_earnings_arithmetic"]["currency"]
        expected["reported_earnings_arithmetic"]["currency_label_omitted"] = True
        expected.update(human_earnings_established=False, poverty_reduction_established=False,
                        financial_authority=False)
        self.assertEqual(actual, expected)

    def test_missing_packet_remains_not_established_not_an_invalid_or_zero_outcome(self):
        for data in ({}, None):
            rc, result = self.from_data(data)
            self.assertEqual(rc, 0)
            for key in ("earned_income_packet", "household_comparison_packet", "poverty_impact_evaluation_packet"):
                self.assertEqual(result[key]["state"], UNKNOWN)
                self.assertEqual(result[key], classify(data)[key])
            self.assertNotIn("reported_earnings_arithmetic", result)

    def test_negative_and_already_deducted_arithmetic_preserved(self):
        for cost, deducted, net in (("1100", False, "-100"), ("100", True, "1000"),
                                    ("100", False, "900")):
            data = packet()
            data["job"]["worker_costs"]["taxes"].update(amount=cost, already_deducted_from_payout=deducted)
            rc, result = self.from_data(data)
            self.assertEqual(rc, 0)
            self.assertEqual(result["reported_earnings_arithmetic"]["net_cash"], net)
            self.assertEqual(result["earned_income_packet"], classify(data)["earned_income_packet"])

    def test_unsupported_fields_and_malformed_types_fail_without_echo(self):
        cases = ["PRIVATE_SENTINEL", [], {"PRIVATE_SENTINEL": 1}]
        for section in ("context", "job", "baseline", "followup", "poverty_line", "counterfactual", "harms"):
            data = packet(); data[section]["PRIVATE_SENTINEL"] = "PRIVATE_SENTINEL"
            cases.append(data)
        data = packet(); data["job"]["consent"] = "PRIVATE_SENTINEL"; cases.append(data)
        for data in cases:
            rc, result = self.from_data(data)
            self.assertEqual((rc, result["status"]), (2, "INVALID_PACKET"))

    def test_read_parse_encoding_depth_and_large_integer_failures_private(self):
        with tempfile.TemporaryDirectory(prefix="PRIVATE_SENTINEL_") as directory:
            path = Path(directory) / "packet.json"
            for raw in (b'PRIVATE_SENTINEL', b'\xffPRIVATE_SENTINEL', b'[' * 10000 + b']' * 10000,
                        b'1' * 10000, b' ' * (MAX_RECORD_BYTES + 1)):
                path.write_bytes(raw)
                rc, result = self.cli([str(path)])
                self.assertEqual((rc, result["status"]), (2, "INVALID_PACKET"))
            for target in (str(Path(directory) / "missing.json"), directory, "PRIVATE_SENTINEL\x00"):
                rc, result = self.cli([target])
                self.assertEqual((rc, result["status"]), (2, "INVALID_PACKET"))

    def test_duplicate_members_and_nonstandard_literals_reject(self):
        raw = json.dumps(packet())
        cases = [raw[:-1] + ',"job":{}}',
                 raw.replace('"local_currency": "NLE"',
                             '"local_currency":"PRIVATE_SENTINEL","local_currency":"NLE"')]
        for literal in ("NaN", "Infinity", "-Infinity"):
            cases.append(raw.replace('"amount": "1000"', '"amount":' + literal))
        with tempfile.TemporaryDirectory(prefix="PRIVATE_SENTINEL_") as directory:
            path = Path(directory) / "packet.json"
            for text in cases:
                path.write_text(text, encoding="utf-8")
                rc, result = self.cli([str(path)])
                self.assertEqual((rc, result["status"]), (2, "INVALID_PACKET"))

    def test_argument_errors_private_and_help_keeps_normal_exit(self):
        for argv in ([], ["--PRIVATE_SENTINEL"], ["packet.json", "PRIVATE_SENTINEL"]):
            rc, result = self.cli(argv)
            self.assertEqual((rc, result["status"]), (2, "INVALID_PACKET"))
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr), self.assertRaises(SystemExit) as caught:
            main(["--help"])
        self.assertEqual(caught.exception.code, 0)
        self.assertEqual(stderr.getvalue(), "")
        self.assertIn("human_outcome_gate.py", stdout.getvalue())
        self.assertIn("packet", stdout.getvalue())

    def test_size_boundary_preserves_classification_and_next_byte_rejects(self):
        with tempfile.TemporaryDirectory(prefix="PRIVATE_SENTINEL_") as directory:
            path = Path(directory) / "packet.json"
            path.write_bytes(b'{}' + b' ' * (MAX_RECORD_BYTES - 2))
            rc, result = self.cli([str(path)])
            self.assertEqual(rc, 0)
            path.write_bytes(b'{}' + b' ' * (MAX_RECORD_BYTES - 1))
            rc, result = self.cli([str(path)])
            self.assertEqual((rc, result["status"]), (2, "INVALID_PACKET"))

    def test_decimal_arithmetic_exceptions_do_not_escape_cli(self):
        data = packet(); data["job"]["worker_costs"]["other"]["amount"] = "1e1000000"
        rc, result = self.from_data(data)
        self.assertEqual((rc, result["status"]), (2, "INVALID_PACKET"))

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO unavailable on this platform")
    def test_all_three_clis_reject_fifo_from_another_working_directory(self):
        with tempfile.TemporaryDirectory(prefix="PRIVATE_SENTINEL_") as directory:
            path = Path(directory) / "packet.fifo"
            os.mkfifo(path)
            for script, code in (("metrics/human_outcome_gate.py", 2),
                                 ("experiments/paid-work-channel-qualification/quote_consistency.py", 1),
                                 ("experiments/paid-work-channel-qualification/qualification.py", 1)):
                run = subprocess.run([sys.executable, str(ROOT / script), str(path)],
                                     cwd=directory, capture_output=True, text=True, timeout=2)
                self.assertEqual(run.returncode, code)
                self.assertEqual(run.stderr, "")
                self.assertNotIn("PRIVATE_SENTINEL", run.stdout)
                self.assertTrue(json.loads(run.stdout)["errors"])

    def test_legacy_forwarder_uses_same_reader_and_bound(self):
        sys.path.insert(0, str(ROOT / "experiments/paid-work-channel-qualification"))
        import record_input
        self.assertIs(record_input.read_record, read_record)
        self.assertEqual(record_input.MAX_RECORD_BYTES, MAX_RECORD_BYTES)


if __name__ == "__main__":
    unittest.main()
