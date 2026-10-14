"""Synthetic recovery CLI boundary controls; no RPC, keys or fund movement."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import source_recovery_gate as gate
from scripts.record_input import MAX_RECORD_BYTES, _unique_object
from test_source_recovery_gate import synthetic_ready

CLI = Path(__file__).resolve().with_name("source_recovery_gate.py")
PRIVATE = "PRIVATE_RECOVERY_SENTINEL"


class SourceRecoveryCLITests(unittest.TestCase):
    def call(self, args, *, cwd=None, int_limit=None):
        command = [sys.executable, str(CLI), *map(str, args)]
        if int_limit is not None:
            program = ("import runpy,sys;sys.set_int_max_str_digits(int(sys.argv[1]));"
                       "sys.argv=sys.argv[2:];runpy.run_path(sys.argv[0],run_name='__main__')")
            command = [sys.executable, "-c", program, str(int_limit), str(CLI), *map(str, args)]
        result = subprocess.run(command, cwd=cwd,
                                capture_output=True, text=True, timeout=2)
        self.assertNotIn(PRIVATE, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        return result.returncode, json.loads(result.stdout)

    def raw(self, data):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / (PRIVATE + ".json")
            path.write_bytes(data)
            return self.call([path], cwd=folder)

    def rejected(self, data):
        rc, result = self.raw(data)
        self.assertEqual((rc, result["state"]), (1, "INVALID_PACKET"))
        for flag in ("recovery_verified", "human_earnings_established", "transaction_authorized"):
            self.assertIs(result[flag], False)
        return result

    def test_ready_result_exactly_matches_existing_api_from_other_directory(self):
        packet = synthetic_ready()
        before = copy.deepcopy(packet)
        rc, result = self.raw(json.dumps(packet).encode())
        self.assertEqual(rc, 0)
        self.assertEqual(result, gate.classify(packet))
        self.assertEqual(packet, before)

    def test_missing_receipts_keep_not_established_and_false_flags(self):
        packet = synthetic_ready()
        del packet["deposit_receipt"]
        rc, result = self.raw(json.dumps(packet).encode())
        self.assertEqual((rc, result["state"]), (1, "NOT_ESTABLISHED"))
        self.assertEqual(result, gate.classify(packet))

    def test_wrong_owner_and_unsupported_fields_still_reject_without_echo(self):
        packet = synthetic_ready()
        packet[PRIVATE] = PRIVATE
        self.rejected(json.dumps(packet).encode())
        packet = synthetic_ready()
        packet["deposit_transaction"]["from"] = packet["binding"]["source_funder"]
        self.rejected(json.dumps(packet).encode())

    def test_arguments_and_unreadable_paths_are_structured(self):
        with tempfile.TemporaryDirectory() as folder:
            missing = Path(folder) / PRIVATE
            for args in ([], [missing], [missing, PRIVATE], ["--" + PRIVATE], [folder]):
                rc, result = self.call(args, cwd=folder)
                self.assertEqual((rc, result["state"]), (1, "INVALID_PACKET"))

    @unittest.skipUnless(hasattr(os, "mkfifo"), "POSIX named-pipe control")
    def test_named_pipe_rejects_without_waiting_for_writer(self):
        with tempfile.TemporaryDirectory() as folder:
            fifo = Path(folder) / PRIVATE
            os.mkfifo(fifo)
            rc, result = self.call([fifo], cwd=folder)
            self.assertEqual((rc, result["state"]), (1, "INVALID_PACKET"))

    def test_invalid_utf8_json_depth_and_large_integer_have_static_failure(self):
        for raw in (b"\xff", b"{"):
            result = self.rejected(raw)
            self.assertEqual(result["gaps"], ["unreadable or invalid JSON packet"])
        # Deep arrays are valid JSON too. A decoder with sufficient capacity
        # can reach the existing static wrong-root rejection instead.
        result = self.rejected(b"[" * 20000 + b"]" * 20000)
        self.assertIn(result["gaps"], [["unreadable or invalid JSON packet"],
                                     gate.classify([])["gaps"]])
        # A large integer is standard JSON. Whether it reaches the unchanged
        # packet classifier depends on this interpreter's configured digit limit.
        result = self.rejected(b'{"n":' + b"1" * 5000 + b"}")
        self.assertIn(result["gaps"], [["unreadable or invalid JSON packet"],
                                     gate.classify({"n": 0})["gaps"]])

    @unittest.skipUnless(hasattr(sys, "set_int_max_str_digits"), "configurable integer limit")
    def test_integer_digit_limit_enabled_and_disabled_remain_private_rejections(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / (PRIVATE + ".json")
            path.write_bytes(b'{"n":' + b"1" * 5000 + b"}")
            for limit in (4300, 0):
                rc, result = self.call([path], cwd=folder, int_limit=limit)
                self.assertEqual((rc, result["state"]), (1, "INVALID_PACKET"))
                expected = (["unreadable or invalid JSON packet"] if limit else
                            gate.classify({"n": 0})["gaps"])
                self.assertEqual(result["gaps"], expected)
                for flag in ("recovery_verified", "human_earnings_established", "transaction_authorized"):
                    self.assertIs(result[flag], False)

    def test_nested_duplicates_and_nonstandard_numbers_reject_even_unused_fields(self):
        ready = json.dumps(synthetic_ready())
        for constant in ("NaN", "Infinity", "-Infinity"):
            packet = synthetic_ready()
            packet["return_transaction"]["unused"] = float(constant)
            self.assertEqual(gate.classify(packet)["state"], "READY_FOR_CHAIN_REVIEW")
            self.rejected(json.dumps(packet).encode())
        for raw in ('{"x":{"n":1,"n":2}}', ready.replace('"schema_version": 1',
                    '"schema_version": 1, "schema_version": 1')):
            self.rejected(raw.encode())

    def test_exact_one_mib_boundary_and_next_byte(self):
        raw = json.dumps(synthetic_ready()).encode()
        raw += b" " * (MAX_RECORD_BYTES - len(raw))
        self.assertEqual(self.raw(raw)[0], 0)
        self.rejected(raw + b" ")

    def test_legacy_hook_uses_shared_duplicate_policy(self):
        self.assertEqual(gate.unique_object([("a", 1)]), _unique_object([("a", 1)]))
        with self.assertRaises(ValueError):
            gate.unique_object([(PRIVATE, 1), (PRIVATE, 2)])

    def test_help_is_static_normal_zero_exit(self):
        result = subprocess.run([sys.executable, str(CLI), "--help"], capture_output=True,
                                text=True, timeout=2)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertIn("source_recovery_gate.py", result.stdout)


if __name__ == "__main__":
    unittest.main()
