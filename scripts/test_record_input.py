"""Offline descriptor-bound reader controls, including deterministic FIFO race."""
import errno
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import record_input as reader


class OpenedRecordTests(unittest.TestCase):
    def read(self, path):
        return reader.read_record([str(path)], prog="record-test", description="synthetic")

    def test_regular_file_parity_and_exact_byte_bound(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "record.json"
            raw = b'{"x":1}'
            path.write_bytes(raw + b" " * (reader.MAX_RECORD_BYTES - len(raw)))
            self.assertEqual(self.read(path), {"x": 1})
            path.write_bytes(raw + b" " * (reader.MAX_RECORD_BYTES + 1 - len(raw)))
            with self.assertRaises(ValueError):
                self.read(path)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink support")
    def test_regular_file_symlink_remains_supported(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "record.json"
            path.write_text('{"x":1}')
            link = Path(folder) / "link.json"
            try:
                link.symlink_to(path)
            except OSError:
                self.skipTest("symlink creation not permitted")
            self.assertEqual(self.read(link), {"x": 1})

    def test_opened_nonregular_descriptor_rejects_and_closes(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "record.json"
            path.write_text('{}')
            captured = []
            original_open, original_fstat = os.open, os.fstat
            def tracked_open(name, flags):
                fd = original_open(name, flags)
                captured.append(fd)
                return fd
            with patch.object(reader.os, "open", tracked_open), patch.object(
                    reader.os, "fstat", return_value=SimpleNamespace(st_mode=stat.S_IFDIR)):
                with self.assertRaises(ValueError):
                    self.read(path)
            self.assertEqual(len(captured), 1)
            with self.assertRaises(OSError) as failure:
                original_fstat(captured[0])
            self.assertEqual(failure.exception.errno, errno.EBADF)

    def test_duplicate_and_nonstandard_literal_policies_unchanged(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "record.json"
            for raw in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'):
                path.write_text(raw)
                with self.assertRaises(ValueError):
                    self.read(path)

    @unittest.skipUnless(hasattr(os, "mkfifo") and hasattr(os, "O_NONBLOCK"),
                         "POSIX nonblocking FIFO control")
    def test_regular_to_fifo_after_stat_rejects_without_writer_or_echo(self):
        program = '''import os,sys
from pathlib import Path
from unittest.mock import patch
from metrics.source_recovery_gate import main
p=Path(sys.argv[1]); original=Path.stat
def race(self,*a,**k):
 s=original(self,*a,**k)
 if self==p:
  self.unlink(); os.mkfifo(self)
 return s
with patch.object(Path,"stat",race):
 raise SystemExit(main([str(p)]))
'''
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "PRIVATE_RACE_SENTINEL.json"
            path.write_text('{}')
            run = subprocess.run([sys.executable, "-c", program, str(path)],
                                 cwd=Path(__file__).resolve().parents[1],
                                 capture_output=True, text=True, timeout=2)
            self.assertEqual(run.returncode, 1)
            self.assertEqual(run.stderr, "")
            self.assertNotIn("PRIVATE_RACE_SENTINEL", run.stdout)
            result = json.loads(run.stdout)
            self.assertEqual(result["state"], "INVALID_PACKET")
            for flag in ("recovery_verified", "human_earnings_established", "transaction_authorized"):
                self.assertIs(result[flag], False)

    @unittest.skipUnless(hasattr(os, "mkfifo") and hasattr(os, "O_NONBLOCK"),
                         "POSIX nonblocking FIFO control")
    def test_fifo_race_direct_reader_raises_regular_file_error(self):
        program = '''import os,sys
from pathlib import Path
from unittest.mock import patch
from scripts.record_input import read_record
p=Path(sys.argv[1]); original=Path.stat
def race(self,*a,**k):
 s=original(self,*a,**k)
 if self==p:
  self.unlink(); os.mkfifo(self)
 return s
with patch.object(Path,"stat",race):
 try: read_record([str(p)],prog="probe",description="synthetic")
 except ValueError as error:
  assert str(error)=="record must be a regular file"
  print("REJECTED")
'''
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "record.json"
            path.write_text('{}')
            run = subprocess.run([sys.executable, "-c", program, str(path)],
                                 cwd=Path(__file__).resolve().parents[1],
                                 capture_output=True, text=True, timeout=2)
            self.assertEqual((run.returncode, run.stdout, run.stderr), (0, "REJECTED\n", ""))


if __name__ == "__main__":
    unittest.main()
