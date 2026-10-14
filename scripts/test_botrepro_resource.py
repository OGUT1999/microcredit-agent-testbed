"""Bounded benchmark method controls, not worker-income evidence."""
from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import botrepro_resource as b


class ResourceBenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.packet = json.loads(b.PACKET.read_bytes())

    def call(self, args):
        out = io.StringIO()
        with redirect_stdout(out):
            code = b.main(args)
        return code, out.getvalue()

    def test_immutable_audit_and_summary(self):
        result = b.audit(self.packet)
        self.assertEqual(result['source_subset_bytes'], 49889)
        self.assertAlmostEqual(result['summary']['wall_seconds']['median'], 0.0735205)
        self.assertEqual(result['decision'], 'HOST_SPECIFIC_ONLY_NO_OFFER')

    def test_default_does_not_launch_child(self):
        with patch.object(b.subprocess, 'Popen', side_effect=AssertionError('not a trial')):
            code, out = self.call([])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)['status'], 'AUDIT_PASS')

    def test_invalid_arguments_reject_without_echo_or_launch(self):
        cases = (['--trials', '0'], ['--trials', '-1'], ['--trials', '13'],
                 ['--trials', 'bad'], ['--timeout', 'nan'], ['--timeout', 'inf'],
                 ['--timeout', '0'], ['--timeout', '16'], ['/PRIVATE_SENTINEL'],
                 ['--command', '/PRIVATE_SENTINEL'])
        with patch.object(b.subprocess, 'Popen', side_effect=AssertionError('not a trial')):
            for args in cases:
                code, out = self.call(args)
                self.assertEqual(code, 1)
                self.assertEqual(json.loads(out)['reason'], 'BENCHMARK_CHECK_FAILED')
                self.assertNotIn('PRIVATE_SENTINEL', out)

    def test_packet_hash_guard(self):
        with patch.object(Path, 'read_bytes', return_value=b'{"private":"PRIVATE_SENTINEL"}'):
            code, out = self.call([])
        self.assertEqual(code, 1)
        self.assertNotIn('PRIVATE_SENTINEL', out)

    def test_pin_drift_before_execution(self):
        self.packet['source_subset'][0]['sha256'] = '0' * 64
        with patch.object(b.subprocess, 'run', side_effect=AssertionError('not a baseline')):
            with self.assertRaises(b.Rejected):
                b.reproduce(self.packet, 1, 1)

    def test_summary_tamper_or_missing_trial_rejects(self):
        for mutate in (lambda p: p['summary']['wall_seconds'].update(median=9),
                       lambda p: p['trials'].pop(),
                       lambda p: p['trials'][0].update(trial=12),
                       lambda p: p.update(currency_price=0)):
            packet = deepcopy(self.packet)
            mutate(packet)
            with self.assertRaises(b.Rejected):
                b.audit(packet)

    def test_invalid_measurement_values(self):
        for value in (True, -1, float('nan'), float('inf'), 'PRIVATE_SENTINEL'):
            rows = deepcopy(self.packet['trials'])
            rows[0]['wall_seconds'] = value
            with self.assertRaises(b.Rejected):
                b.summarize(rows)

    def test_nonlinux_rejects_before_trial(self):
        with patch.object(b.sys, 'platform', 'darwin'), patch.object(b.subprocess, 'run') as run:
            with self.assertRaises(b.Rejected):
                b.reproduce(self.packet, 1, 1)
            run.assert_not_called()

    def test_baseline_nonzero_wrong_count_and_missing_ok_reject(self):
        for rc, stderr in ((1, 'PRIVATE_SENTINEL'), (0, 'Ran 0 tests in 0s\nOK\n'),
                           (0, 'Ran 11 tests in 0s\nFAILED\n')):
            with patch.object(b.subprocess, 'run', return_value=SimpleNamespace(returncode=rc, stderr=stderr)):
                with self.assertRaises(b.Rejected):
                    b.reproduce(self.packet, 1, 1)

    def test_baseline_timeout_redacts(self):
        with patch.object(b.subprocess, 'run', side_effect=subprocess.TimeoutExpired('PRIVATE_SENTINEL', 1)):
            code, out = self.call(['--run', '--trials', '1'])
        self.assertEqual(code, 1)
        self.assertNotIn('PRIVATE_SENTINEL', out)

    @unittest.skipUnless(sys.platform == 'linux' and hasattr(os, 'wait4'), 'Linux wait4')
    def test_actual_child_success(self):
        result = b.measure([sys.executable, '-c', 'pass'], 1)
        self.assertGreater(result['wall_seconds'], 0)
        self.assertGreater(result['maxrss_kib'], 0)

    @unittest.skipUnless(sys.platform == 'linux' and hasattr(os, 'wait4'), 'Linux wait4')
    def test_nonzero_child_and_signal_reject_without_double_wait(self):
        for command in ('raise SystemExit(7)', 'import os,signal; os.kill(os.getpid(), signal.SIGTERM)'):
            with self.assertRaises(b.Rejected):
                b.measure([sys.executable, '-c', command], 1)

    @unittest.skipUnless(sys.platform == 'linux' and hasattr(os, 'wait4'), 'Linux wait4')
    def test_timeout_kills_and_reaps_owned_child(self):
        seen = []
        original = b.subprocess.Popen
        def spawn(*args, **kwargs):
            p = original(*args, **kwargs)
            seen.append(p)
            return p
        with patch.object(b.subprocess, 'Popen', side_effect=spawn):
            with self.assertRaises(b.Rejected):
                b.measure([sys.executable, '-c', 'import time; time.sleep(10)'], 0.02)
        self.assertEqual(seen[0].returncode, -9)
        with self.assertRaises(ChildProcessError):
            os.wait4(seen[0].pid, os.WNOHANG)

    def test_os_failure_redacts_exception(self):
        with patch.object(Path, 'read_bytes', side_effect=OSError('/PRIVATE_SENTINEL')):
            code, out = self.call([])
        self.assertEqual(code, 1)
        self.assertNotIn('PRIVATE_SENTINEL', out)


if __name__ == '__main__':
    unittest.main()
