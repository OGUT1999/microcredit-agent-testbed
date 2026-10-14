#!/usr/bin/env python3
"""Audit immutable BOT-REPRO-002 observations; opt-in bounded Linux reproduction.

AI author: Codex. No account, network, payment or arbitrary-command interface.
"""
import argparse
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import signal
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'evidence/botrepro002-resource-20261014/observation.json'
OBSERVATION_SHA256 = 'ee5c4ec8ac0522d7ddb12cff109953bae7902630a319fc435066c5cabfee75fd'
COMMAND = ('-m', 'unittest', 'discover', '-s', 'metrics', '-p', 'test_human_outcome_cash.py', '-v')
FIELDS = ('wall_seconds', 'user_cpu_seconds', 'system_cpu_seconds', 'maxrss_kib')
POLL = 0.002


class Rejected(Exception):
    """Generic failure, intentionally never include paths or child diagnostics."""


def pins_match(packet, root=ROOT):
    # Fixed trusted historical packet, not an arbitrary path/command API.
    for pin in packet['source_subset']:
        raw = (root / pin['path']).read_bytes()
        if len(raw) != pin['bytes'] or hashlib.sha256(raw).hexdigest() != pin['sha256']:
            raise Rejected()
    return sum(p['bytes'] for p in packet['source_subset'])


def summarize(trials):
    if not trials:
        raise Rejected()
    result = {}
    for field in FIELDS:
        values = [t[field] for t in trials]
        if any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in values):
            raise Rejected()
        median = float(statistics.median([Decimal(str(v)) for v in values]))
        result[field] = dict(minimum=min(values), median=median, maximum=max(values))
    return result


def audit(packet):
    if len(packet['trials']) != 12 or [t['trial'] for t in packet['trials']] != list(range(1, 13)):
        raise Rejected()
    result = summarize(packet['trials'])
    for field in FIELDS:
        for statistic, actual in result[field].items():
            expected = packet['summary'][field][statistic]
            if type(expected) not in (int, float) or not math.isfinite(expected) or not math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12):
                raise Rejected()
    if any(packet[key] is not None for key in ('currency_price', 'worker_effort', 'full_owner_cost')):
        raise Rejected()
    return {'status': 'AUDIT_PASS', 'trials': 12, 'source_subset_bytes': pins_match(packet),
            'summary': result, 'decision': 'HOST_SPECIFIC_ONLY_NO_OFFER'}


def terminate_and_reap(proc):
    # Own process session only; no unrelated PID/worker cleanup.
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    _, status, usage = os.wait4(proc.pid, 0)
    proc.returncode = os.waitstatus_to_exitcode(status)
    return usage


def measure(command, timeout):
    start = time.perf_counter()
    proc = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, start_new_session=True)
    reaped = False
    try:
        while True:
            pid, status, usage = os.wait4(proc.pid, os.WNOHANG)
            if pid:
                proc.returncode = os.waitstatus_to_exitcode(status)
                reaped = True
                if proc.returncode != 0:
                    raise Rejected()
                return dict(wall_seconds=time.perf_counter() - start,
                            user_cpu_seconds=usage.ru_utime, system_cpu_seconds=usage.ru_stime,
                            maxrss_kib=usage.ru_maxrss)
            if time.perf_counter() - start >= timeout:
                raise Rejected()
            time.sleep(POLL)
    finally:
        if not reaped:
            terminate_and_reap(proc)


def reproduce(packet, trials, timeout):
    if sys.platform != 'linux' or not hasattr(os, 'wait4'):
        raise Rejected()
    pins_match(packet)  # Fail drift before launching code.
    command = [sys.executable, *COMMAND]
    try:
        baseline = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise Rejected() from None
    if baseline.returncode != 0 or not re.search(r'^Ran 11 tests in ', baseline.stderr, re.M) or not re.search(r'^OK$', baseline.stderr, re.M):
        raise Rejected()
    rows = [dict(trial=i+1, **measure(command, timeout)) for i in range(trials)]
    return {'status': 'REPRODUCTION_PASS', 'checked_at': datetime.now(timezone.utc).isoformat(),
            'runtime': {'implementation': platform.python_implementation(), 'python': platform.python_version(),
                        'os': 'Linux', 'architecture': platform.machine()},
            'method': 'fresh-process after one prewarming baseline; 2ms poll; Linux wait4; no cache flush',
            'trials': rows, 'summary': summarize(rows), 'currency_price': None,
            'worker_effort': None, 'full_owner_cost': None, 'network_instrumented': False,
            'decision': 'HOST_SPECIFIC_ONLY_NO_OFFER'}


class PrivateParser(argparse.ArgumentParser):
    def error(self, message):
        raise Rejected()


def main(argv=None):
    try:
        parser = PrivateParser(description=__doc__)
        parser.add_argument('--run', action='store_true', help='opt in to new distinct Linux observations')
        parser.add_argument('--trials', type=int, default=12)
        parser.add_argument('--timeout', type=float, default=15.0)
        args = parser.parse_args(argv)
        if not 1 <= args.trials <= 12 or not math.isfinite(args.timeout) or not 0.01 <= args.timeout <= 15:
            raise Rejected()
        raw = PACKET.read_bytes()
        if hashlib.sha256(raw).hexdigest() != OBSERVATION_SHA256:
            raise Rejected()
        packet = json.loads(raw)
        result = audit(packet)
        if args.run:
            result = reproduce(packet, args.trials, args.timeout)
        print(json.dumps(result, sort_keys=True, allow_nan=False))
        return 0
    except (Rejected, OSError, ValueError, KeyError, TypeError, ChildProcessError):
        print('{"status":"REJECTED","reason":"BENCHMARK_CHECK_FAILED"}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
