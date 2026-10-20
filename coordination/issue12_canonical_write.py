#!/usr/bin/env python3
"""Exact writer for canonical issue-12 comment 5999201336 (candidate; no authority by itself).

Replaces the comment body with one reviewed candidate file, once, under a lease the CALLER
already holds (git-explicit-lease-v2, `coordination/run_lock.py`). It never acquires or
releases the lease and creates no cursor, schedule, ledger or second protocol.

Every gate is an explicit `if ... raise`, never `assert`, and the module refuses to start
under `-O` or `PYTHONOPTIMIZE`, so no check can be optimized away.

Order: candidate hash, UTF-8 and length, public-content check, first read (expected body
hash and `updated_at`), optional verify command, final reread, owned-lease check, one PATCH,
fresh readback (exact bytes, length, optional verify command). A refusal before the PATCH
changes nothing. After a PATCH attempt that fails or reads back wrong the outcome is
UNCERTAIN: the tool reports what the comment holds and stops; it never retries or rolls back.

Scope, stated plainly: the lease serializes cooperating writers only. GitHub documents no
conditional write for the issue-comment PATCH, so an edit by a noncooperating writer made
between the final read and the PATCH would be overwritten, and a readback equal to the
candidate cannot show otherwise. This tool narrows that window; it cannot close it.
Status contract. Exit 0: APPLIED, DRY_RUN_OK, or ALREADY_APPLIED (the live bytes equal the candidate, the
caller still owns the lease and the verify command, if any, passed again with the original baseline; with
--no-semantic-verify only the byte checks ran, and the report says semantic_verified false). Exit 2: refused
before any write. Exit 3: UNCERTAIN after a write attempt, including ALREADY_APPLIED_UNVERIFIED (bytes present
but the verify command could not be re-run without --baseline, or failed): reconcile before anything else."""
import sys

if sys.flags.optimize:
    sys.stderr.write('refusing to run under -O or PYTHONOPTIMIZE: every gate here is an explicit check\n')
    raise SystemExit(2)

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request

REPO_SLUG = 'scottonchain/microcredit-agent-testbed'
COMMENT_ID = 5999201336
LIMIT = 65536
SCOPE = ('cooperative lease only; edits by noncooperating writers between the final read '
         'and the PATCH are not detectable')
TOKEN = re.compile(r'[a-z0-9][a-z0-9-]{7,79}')
HEAD = re.compile(r'[0-9a-f]{40}')
SHA = re.compile(r'[0-9a-f]{64}')
LOOPBACK_HOST = '127.0.0.1'
API_HOST = 'api.github.com'
ENDPOINT = '/repos/%s/issues/comments/%d' % (REPO_SLUG, COMMENT_ID)


class Refusal(Exception):
    """Stop before any write; nothing changed."""

    def __init__(self, reason, detail=''):
        Exception.__init__(self, reason)
        self.reason, self.detail = reason, detail


class Uncertain(Exception):
    """A write was attempted; the comment state must be reconciled by a person."""

    def __init__(self, reason, state, detail=''):
        Exception.__init__(self, reason)
        self.reason, self.state, self.detail = reason, state, detail


class ApiError(Exception):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def refuse_optimized():
    if sys.flags.optimize:
        raise Refusal('OPTIMIZED', 'run without -O and without PYTHONOPTIMIZE')


def read_candidate(path, want_sha):
    try:
        data = Path(path).read_bytes()
    except OSError:
        raise Refusal('CANDIDATE_UNREADABLE')
    if sha256_hex(data) != want_sha:
        raise Refusal('CANDIDATE_HASH', 'file bytes differ from --candidate-sha256')
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        raise Refusal('CANDIDATE_ENCODING')
    if not text:
        raise Refusal('CANDIDATE_EMPTY')
    if len(text) > LIMIT:
        raise Refusal('CANDIDATE_SIZE', '%d characters, limit %d' % (len(text), LIMIT))
    return data, text


def check_public_content(repo, candidate_path):
    script = Path(repo) / 'world-model' / 'check-public-content.sh'
    if not script.is_file():
        raise Refusal('PUBLIC_CONTENT_CHECK_MISSING')
    done = subprocess.run(['bash', str(script), '--text', str(candidate_path)],
                          capture_output=True, text=True, cwd=str(repo))
    if done.returncode != 0:
        raise Refusal('PUBLIC_CONTENT', 'check-public-content.sh exited %d' % done.returncode)


def assert_owned(repo, owner, head, helper_sha256=None):
    script = Path(repo) / 'coordination' / 'run_lock.py'
    if helper_sha256 is not None:
        try:
            installed = sha256_hex(script.read_bytes())
        except OSError:
            raise Refusal('LOCK_HELPER_HASH', 'helper unreadable')
        if installed != helper_sha256:
            raise Refusal('LOCK_HELPER_HASH', 'installed run_lock.py differs from --lock-helper-sha256')
    done = subprocess.run([sys.executable, str(script), '--repo', str(repo), 'assert-owned',
                           '--owner', owner, '--acquired-head', head],
                          capture_output=True, text=True)
    if done.returncode != 0:
        raise Refusal('LEASE_NOT_OWNED', 'assert-owned exited %d' % done.returncode)
    try:
        said = json.loads(done.stdout)
    except ValueError:
        raise Refusal('LEASE_NOT_OWNED', 'assert-owned printed no JSON')
    if not isinstance(said, dict) or said.get('owner') != owner or said.get('acquired_head') != head:
        raise Refusal('LEASE_NOT_OWNED', 'assert-owned output does not name the owned head')


def run_verify(repo, command, old_bytes, new_bytes, failure):
    """Run the caller's verify command (a JSON list) with {old} and {new} as file paths."""
    if command is None:
        return
    with tempfile.TemporaryDirectory(prefix='canonical-write-') as directory:
        old_path, new_path = Path(directory) / 'old', Path(directory) / 'new'
        old_path.write_bytes(old_bytes)
        new_path.write_bytes(new_bytes)
        argv = [part.replace('{old}', str(old_path)).replace('{new}', str(new_path)) for part in command]
        done = subprocess.run(argv, capture_output=True, text=True, cwd=str(repo))
    if done.returncode != 0:
        raise failure('VERIFY_FAILED', 'verify command exited %d' % done.returncode)


class Transport:
    """GitHub REST for the one comment. Token from the named environment variable, never printed."""

    def __init__(self, origin, token):
        self.url = origin + ENDPOINT
        self.token = token
        loopback = origin.startswith('http://' + LOOPBACK_HOST)
        handlers = [NoRedirect()] + ([urllib.request.ProxyHandler({})] if loopback else [])
        self.open = urllib.request.build_opener(*handlers).open

    def request(self, method, payload=None):
        data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode('utf-8')
        headers = {'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28',
                   'Authorization': 'Bearer ' + self.token, 'User-Agent': 'issue12-canonical-write'}
        if data is not None:
            headers['Content-Type'] = 'application/json; charset=utf-8'
        req = urllib.request.Request(self.url, data=data, method=method, headers=headers)
        try:
            with self.open(req, timeout=30) as response:
                if response.status != 200:
                    raise ApiError('status %s' % response.status)
                raw = response.read()
        except urllib.error.HTTPError as exc:
            raise ApiError('status %s' % exc.code)
        except (urllib.error.URLError, OSError, ValueError):
            raise ApiError('transport failure')
        try:
            value = json.loads(raw.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            raise ApiError('response is not JSON')
        if not isinstance(value, dict):
            raise ApiError('response is not an object')
        return value

    def read(self):
        value = self.request('GET')
        body, stamp = value.get('body'), value.get('updated_at')
        if not isinstance(body, str) or not isinstance(stamp, str) or not stamp:
            raise ApiError('response lacks body or updated_at')
        try:
            body.encode('utf-8')
        except UnicodeEncodeError:
            raise ApiError('body is not valid Unicode text')
        return body, stamp

    def write(self, text):
        self.request('PATCH', {'body': text})


def check_api_base(base):
    """Return the validated origin. The one endpoint is built from it, never from the raw string."""
    if base != base.strip() or any(ord(c) <= 32 or c in '\\?#@' for c in base):
        raise Refusal('API_BASE', 'origin only: no whitespace, userinfo, query, fragment or backslash')
    try:
        parts = urllib.parse.urlsplit(base)
        port = parts.port
    except ValueError:
        raise Refusal('API_BASE', 'unparseable')
    if parts.path not in ('', '/') or parts.query or parts.fragment or parts.username or parts.password:
        raise Refusal('API_BASE', 'origin only: no path, query, fragment or userinfo')
    if parts.scheme == 'https' and parts.hostname == API_HOST and port is None:
        return 'https://' + API_HOST
    if parts.scheme == 'http' and parts.hostname == LOOPBACK_HOST and port is not None and 1024 <= port <= 65535:
        return 'http://%s:%d' % (LOOPBACK_HOST, port)
    raise Refusal('API_BASE', 'https://%s only (plain http only for %s test ports 1024 to 65535)' % (API_HOST, LOOPBACK_HOST))


def describe(transport, pre_bytes, candidate_bytes):
    """Best-effort state after a failed or doubtful write; never raises."""
    try:
        body, stamp = transport.read()
    except ApiError:
        return {'state': 'UNREADABLE'}
    now = body.encode('utf-8')
    state = 'APPLIED' if now == candidate_bytes else 'NOT_APPLIED' if now == pre_bytes else 'OTHER_CONTENT'
    return {'state': state, 'sha256': sha256_hex(now), 'characters': len(body), 'updated_at': stamp}


def uncertain_after_write(reason, detail=''):
    return Uncertain(reason + '_AFTER_WRITE', {'state': 'APPLIED'}, detail)


def execute(args, progress):
    refuse_optimized()
    if not TOKEN.fullmatch(args.owner):
        raise Refusal('OWNER_TOKEN')
    if not HEAD.fullmatch(args.acquired_head):
        raise Refusal('ACQUIRED_HEAD')
    for name in ('candidate_sha256', 'expected_body_sha256', 'lock_helper_sha256'):
        value = getattr(args, name)
        if value is not None and not SHA.fullmatch(value):
            raise Refusal('SHA256_ARGUMENT', name)
    origin = check_api_base(args.api_base)
    token = os.environ.get(args.token_env, '')
    if not token:
        raise Refusal('TOKEN_MISSING', 'environment variable %s is empty' % args.token_env)
    repo = Path(args.repo).resolve()
    baseline_bytes = None
    if args.baseline is not None:
        try:
            baseline_bytes = Path(args.baseline).read_bytes()
        except OSError:
            raise Refusal('BASELINE_UNREADABLE')
        if sha256_hex(baseline_bytes) != args.expected_body_sha256:
            raise Refusal('BASELINE_HASH', 'baseline bytes differ from --expected-body-sha256')
    candidate_bytes, candidate_text = read_candidate(args.candidate, args.candidate_sha256)
    check_public_content(repo, args.candidate)
    transport = Transport(origin, token)

    try:
        first_body, first_stamp = transport.read()
    except ApiError as exc:
        raise Refusal('API_READ_FAILED', str(exc))
    first_bytes = first_body.encode('utf-8')
    if first_bytes == candidate_bytes:
        assert_owned(repo, args.owner, args.acquired_head, args.lock_helper_sha256)
        if args.verify_cmd is not None:
            if baseline_bytes is None:
                raise Uncertain('ALREADY_APPLIED_UNVERIFIED', {'state': 'APPLIED', 'sha256': sha256_hex(first_bytes)},
                                'the bytes are present but the verify command needs the original baseline (--baseline) '
                                'to run again; byte presence is not semantic verification')
            run_verify(repo, args.verify_cmd, baseline_bytes, first_bytes, uncertain_after_write)
        return {'outcome': 'ALREADY_APPLIED', 'sha256': sha256_hex(candidate_bytes),
                'characters': len(candidate_text), 'updated_at': first_stamp,
                'semantic_verified': args.verify_cmd is not None, 'scope': SCOPE}
    if sha256_hex(first_bytes) != args.expected_body_sha256 or first_stamp != args.expected_updated_at:
        raise Refusal('BODY_CHANGED', 'live body hash or updated_at differs from the values the candidate was built from')
    run_verify(repo, args.verify_cmd, first_bytes, candidate_bytes, Refusal)

    try:
        again_body, again_stamp = transport.read()
    except ApiError as exc:
        raise Refusal('API_READ_FAILED', str(exc))
    if again_body.encode('utf-8') != first_bytes or again_stamp != first_stamp:
        raise Refusal('BODY_CHANGED_BEFORE_PATCH', 'the final reread differs from the first read')
    assert_owned(repo, args.owner, args.acquired_head, args.lock_helper_sha256)
    if args.dry_run:
        return {'outcome': 'DRY_RUN_OK', 'before_sha256': sha256_hex(first_bytes),
                'candidate_sha256': sha256_hex(candidate_bytes), 'scope': SCOPE}

    progress['patch_attempted'] = True
    try:
        transport.write(candidate_text)
    except ApiError as exc:
        raise Uncertain('PATCH_FAILED', describe(transport, first_bytes, candidate_bytes), str(exc))
    try:
        saved_body, saved_stamp = transport.read()
    except ApiError as exc:
        raise Uncertain('READBACK_FAILED', {'state': 'UNREADABLE'}, str(exc))
    saved_bytes = saved_body.encode('utf-8')
    if saved_bytes != candidate_bytes:
        raise Uncertain('READBACK_MISMATCH', describe(transport, first_bytes, candidate_bytes))
    if len(saved_body) > LIMIT:
        raise Uncertain('READBACK_SIZE', describe(transport, first_bytes, candidate_bytes))
    run_verify(repo, args.verify_cmd, first_bytes, saved_bytes, uncertain_after_write)
    return {'outcome': 'APPLIED', 'before_sha256': sha256_hex(first_bytes), 'after_sha256': sha256_hex(saved_bytes),
            'before_characters': len(first_body), 'after_characters': len(saved_body),
            'updated_at_before': first_stamp, 'updated_at_after': saved_stamp,
            'updated_at_advanced': saved_stamp != first_stamp,
            'semantic_verified': args.verify_cmd is not None, 'scope': SCOPE}


def parse(argv):
    here = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--candidate', required=True, help='file holding the exact new body (UTF-8)')
    p.add_argument('--candidate-sha256', required=True, help='sha256 of that file as reviewed')
    p.add_argument('--expected-body-sha256', required=True, help='sha256 of the live body the candidate was built from')
    p.add_argument('--expected-updated-at', required=True, help='live updated_at the candidate was built from')
    p.add_argument('--owner', required=True)
    p.add_argument('--acquired-head', required=True)
    p.add_argument('--repo', default=str(here), help='checkout holding coordination/run_lock.py and world-model/')
    p.add_argument('--api-base', default='https://api.github.com')
    p.add_argument('--token-env', default='GITHUB_TOKEN', help='name of the environment variable holding the token')
    check = p.add_mutually_exclusive_group(required=True)
    check.add_argument('--verify-cmd', default=None, help='JSON list; {old} and {new} become file paths; exit 0 required')
    check.add_argument('--no-semantic-verify', action='store_true',
                       help='say plainly that no semantic check beyond the byte checks is run')
    p.add_argument('--baseline', default=None,
                   help='file holding the original live body (sha256 must equal --expected-body-sha256); lets the '
                        'verify command run again when the candidate is already in place')
    p.add_argument('--lock-helper-sha256', default=None, help='refuse unless run_lock.py has exactly this sha256')
    p.add_argument('--dry-run', action='store_true', help='run every gate up to the PATCH and stop')
    args = p.parse_args(argv)
    if args.verify_cmd is not None:
        try:
            command = json.loads(args.verify_cmd)
        except ValueError:
            p.error('--verify-cmd must be a JSON list of strings')
        if not isinstance(command, list) or not command or not all(isinstance(x, str) for x in command):
            p.error('--verify-cmd must be a non-empty JSON list of strings')
        args.verify_cmd = command
    return args


def main(argv=None):
    progress = {'patch_attempted': False}
    try:
        refuse_optimized()
        args = parse(sys.argv[1:] if argv is None else argv)
        report = execute(args, progress)
    except Refusal as exc:
        print(json.dumps({'outcome': 'REFUSED', 'reason': exc.reason, 'detail': exc.detail}, sort_keys=True))
        return 2
    except Uncertain as exc:
        print(json.dumps({'outcome': 'UNCERTAIN', 'reason': exc.reason, 'comment': exc.state,
                          'detail': exc.detail, 'action': 'stop protected work and reconcile; no retry'}, sort_keys=True))
        return 3
    except Exception as exc:
        kind = type(exc).__name__
        if progress['patch_attempted']:
            print(json.dumps({'outcome': 'UNCERTAIN', 'reason': 'INTERNAL_ERROR_AFTER_WRITE', 'detail': kind,
                              'comment': {'state': 'UNKNOWN'},
                              'action': 'stop protected work and reconcile; no retry'}, sort_keys=True))
            return 3
        print(json.dumps({'outcome': 'REFUSED', 'reason': 'INTERNAL_ERROR', 'detail': kind}, sort_keys=True))
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
