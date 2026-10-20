"""Exercise the exact canonical writer through its real entrypoint, offline.

Each case runs `issue12_canonical_write.py` as a subprocess against a local loopback HTTP
fixture that imitates the one comment, and against a throwaway git remote holding a real
`run_lock.py` lock. Nothing here touches GitHub, the real lock or any real comment."""
import ast
import hashlib
import http.server
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parent.parent
WRITER = ROOT / 'coordination' / 'issue12_canonical_write.py'
PATH = '/repos/scottonchain/microcredit-agent-testbed/issues/comments/5999201336'
TOKEN = 'fixture-token-value-7c1d'
OWNER = 'writer-test-owner'
BODY = '<!-- fixture -->\nstate one\n'
STAMP = '2026-10-20T08:00:00Z'
GIT_ID = ['-c', 'user.name=Fixture', '-c', 'user.email=fixture@users.noreply.github.com']


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Comment:
    def __init__(self, body=BODY, stamp=STAMP):
        self.body, self.stamp = body, stamp
        self.gets = self.patches = 0
        self.fail_get = set()
        self.on_get = None
        self.patch_mode = 'ok'
        self.revision = 0

    def apply(self, text):
        self.body = text
        self.revision += 1
        self.stamp = '2026-10-20T08:00:%02dZ' % (self.revision + 1)


def make_handler(state):
    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send(self, code, payload):
            raw = json.dumps(payload).encode('utf-8')
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def authorized(self):
            return self.path == PATH and self.headers.get('Authorization') == 'Bearer ' + TOKEN

        def do_GET(self):
            if not self.authorized():
                return self.send(401, {'message': 'no'})
            state.gets += 1
            if state.on_get:
                state.on_get(state, state.gets)
            if state.gets in state.fail_get:
                return self.send(500, {'message': 'boom'})
            self.send(200, {'body': state.body, 'updated_at': state.stamp})

        def do_PATCH(self):
            if not self.authorized():
                return self.send(401, {'message': 'no'})
            state.patches += 1
            length = int(self.headers.get('Content-Length', '0'))
            text = json.loads(self.rfile.read(length).decode('utf-8'))['body']
            mode = state.patch_mode
            if mode == 'fail':
                return self.send(500, {'message': 'boom'})
            if mode == 'ignore':
                return self.send(200, {'body': state.body, 'updated_at': state.stamp})
            if mode == 'crlf':
                text = text.replace('\n', '\r\n')
            state.apply(text)
            if mode == 'apply_then_fail':
                return self.send(502, {'message': 'gateway'})
            self.send(200, {'body': state.body, 'updated_at': state.stamp})

    return Handler


class Fixture:
    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='canonical-write-test-')
        self.root = Path(self.tmp.name)
        self.state = Comment()
        self.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), make_handler(self.state))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = 'http://127.0.0.1:%d' % self.server.server_address[1]
        self.work = self.root / 'work'
        self.make_repo()

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.tmp.cleanup()

    def git(self, *args, cwd=None):
        subprocess.run(['git'] + GIT_ID + list(args), cwd=str(cwd or self.work), check=True, capture_output=True)

    def make_repo(self):
        remote = self.root / 'remote.git'
        subprocess.run(['git', 'init', '--bare', '-q', str(remote)], check=True)
        self.work.mkdir()
        self.git('init', '-q', '-b', 'main')
        (self.work / 'coordination').mkdir()
        (self.work / 'world-model').mkdir()
        shutil.copy(ROOT / 'coordination' / 'run_lock.py', self.work / 'coordination' / 'run_lock.py')
        shutil.copy(ROOT / 'world-model' / 'check-public-content.sh', self.work / 'world-model' / 'check-public-content.sh')
        self.git('add', '.')
        self.git('commit', '-q', '-m', 'seed')
        self.git('remote', 'add', 'origin', str(remote))
        self.git('push', '-q', 'origin', 'main')
        (self.work / 'LOCK.json').write_text(json.dumps({'protocol': 'git-explicit-lease-v2', 'state': 'unlocked',
                                                         'owner': None, 'execution': None}))
        self.git('add', 'LOCK.json')
        self.git('commit', '-q', '-m', 'lock')
        self.git('push', '-q', 'origin', 'HEAD:refs/heads/coordination/issue-12-run-lock')

    def lock(self, *args):
        done = subprocess.run([sys.executable, str(self.work / 'coordination' / 'run_lock.py'), '--repo', str(self.work)] + list(args),
                              capture_output=True, text=True)
        return done

    def acquire(self, owner=OWNER, execution='writer-test-exec'):
        done = self.lock('acquire', '--owner', owner, '--execution', execution)
        if done.returncode != 0:
            raise RuntimeError('acquire failed')
        return json.loads(done.stdout)['acquired_head']

    def release(self, head, owner=OWNER):
        if self.lock('release', '--owner', owner, '--acquired-head', head).returncode != 0:
            raise RuntimeError('release failed')

    def default_head(self):
        if not hasattr(self, 'cached_head'):
            self.cached_head = self.acquire()
        return self.cached_head

    def candidate(self, text, name='candidate.txt'):
        path = self.root / name
        path.write_bytes(text.encode('utf-8') if isinstance(text, str) else text)
        return path

    def run(self, candidate_text='<!-- fixture -->\nstate two\n', head=None, mode='normal', verify=None, dry=False,
            token=TOKEN, base=None, expected_body=BODY, expected_stamp=STAMP, candidate_sha=None, owner=OWNER,
            candidate_bytes=None):
        data = candidate_bytes if candidate_bytes is not None else candidate_text.encode('utf-8')
        path = self.candidate(data)
        head = head or self.default_head()
        argv = [sys.executable] + (['-O'] if mode == 'O' else ['-OO'] if mode == 'OO' else []) + [str(WRITER),
                '--candidate', str(path), '--candidate-sha256', candidate_sha or sha(data),
                '--expected-body-sha256', sha(expected_body.encode('utf-8')), '--expected-updated-at', expected_stamp,
                '--owner', owner, '--acquired-head', head, '--repo', str(self.work),
                '--api-base', base or self.base]
        if verify is not None:
            argv += ['--verify-cmd', json.dumps(verify)]
        if dry:
            argv.append('--dry-run')
        env = {k: v for k, v in os.environ.items() if k not in ('PYTHONOPTIMIZE', 'GITHUB_TOKEN')}
        if mode == 'env2':
            env['PYTHONOPTIMIZE'] = '2'
        if token is not None:
            env['GITHUB_TOKEN'] = token
        done = subprocess.run(argv, capture_output=True, text=True, env=env)
        try:
            report = json.loads(done.stdout) if done.stdout.strip() else None
        except ValueError:
            report = None
        return done.returncode, report, done


class CanonicalWriterTests(unittest.TestCase):
    def setUp(self):
        self.fx = Fixture()
        self.addCleanup(self.fx.close)

    def refused(self, reason, **kwargs):
        code, report, done = self.fx.run(**kwargs)
        self.assertEqual(code, 2, done.stdout + done.stderr)
        self.assertEqual(report['outcome'], 'REFUSED')
        self.assertEqual(report['reason'], reason)
        self.assertEqual(self.fx.state.patches, 0)
        self.assertEqual(self.fx.state.body, BODY)
        return report

    def uncertain(self, reason, **kwargs):
        code, report, done = self.fx.run(**kwargs)
        self.assertEqual(code, 3, done.stdout + done.stderr)
        self.assertEqual(report['outcome'], 'UNCERTAIN')
        self.assertEqual(report['reason'], reason)
        self.assertEqual(self.fx.state.patches, 1, 'a failed write must never be retried')
        return report

    def test_clean_apply_writes_exact_bytes_once(self):
        text = '<!-- fixture -->\nstate two é\n'
        code, report, done = self.fx.run(candidate_text=text)
        self.assertEqual(code, 0, done.stdout + done.stderr)
        self.assertEqual(report['outcome'], 'APPLIED')
        self.assertEqual(self.fx.state.body.encode('utf-8'), text.encode('utf-8'))
        self.assertEqual(self.fx.state.patches, 1)
        self.assertEqual(report['after_sha256'], sha(text.encode('utf-8')))
        self.assertEqual(report['before_sha256'], sha(BODY.encode('utf-8')))
        self.assertTrue(report['updated_at_advanced'])
        self.assertIn('cooperative', report['scope'])
        self.assertNotIn(TOKEN, done.stdout + done.stderr)

    def test_duplicate_run_is_a_no_op(self):
        head = self.fx.acquire()
        first = self.fx.run(head=head)
        self.assertEqual(first[0], 0)
        second = self.fx.run(head=head)
        self.assertEqual(second[0], 0)
        self.assertEqual(second[1]['outcome'], 'ALREADY_APPLIED')
        self.assertEqual(self.fx.state.patches, 1)

    def test_dry_run_stops_before_patch(self):
        code, report, done = self.fx.run(dry=True)
        self.assertEqual(code, 0, done.stdout + done.stderr)
        self.assertEqual(report['outcome'], 'DRY_RUN_OK')
        self.assertEqual(self.fx.state.patches, 0)
        self.assertEqual(self.fx.state.gets, 2)

    def test_optimized_interpreters_refuse_before_any_network_call(self):
        for mode in ('O', 'OO', 'env2'):
            with self.subTest(mode=mode):
                code, report, done = self.fx.run(mode=mode)
                self.assertEqual(code, 2, done.stdout + done.stderr)
                self.assertIn('refusing', done.stderr)
                self.assertEqual((self.fx.state.gets, self.fx.state.patches), (0, 0))
                self.assertEqual(self.fx.state.body, BODY)

    def test_optimized_run_is_refused_even_for_a_would_be_stale_body(self):
        self.fx.state.body, self.fx.state.stamp = 'someone else edited\n', '2026-10-20T08:05:00Z'
        code, report, done = self.fx.run(mode='O')
        self.assertEqual(code, 2)
        self.assertEqual((self.fx.state.gets, self.fx.state.patches), (0, 0))

    def test_candidate_bytes_must_match_the_reviewed_hash(self):
        self.refused('CANDIDATE_HASH', candidate_sha='0' * 64)

    def test_candidate_must_be_utf8_nonempty_and_within_the_limit(self):
        self.refused('CANDIDATE_ENCODING', candidate_bytes=b'\xff\xfe broken')
        self.refused('CANDIDATE_EMPTY', candidate_bytes=b'')
        self.refused('CANDIDATE_SIZE', candidate_text='x' * 65537)
        self.assertEqual(self.fx.state.gets, 0)

    def test_candidate_at_the_limit_is_accepted(self):
        code, report, done = self.fx.run(candidate_text='y' * 65536)
        self.assertEqual(code, 0, done.stdout + done.stderr)
        self.assertEqual(len(self.fx.state.body), 65536)

    def test_public_content_check_blocks_a_forbidden_token_shape(self):
        forbidden = 'gh' + 'p_' + 'A' * 24
        self.refused('PUBLIC_CONTENT', candidate_text='ok\n' + forbidden + '\n')

    def test_changed_body_or_timestamp_since_the_read_refuses(self):
        self.refused('BODY_CHANGED', expected_body='older body\n')
        self.refused('BODY_CHANGED', expected_stamp='2026-10-20T07:59:59Z')

    def test_concurrent_edit_between_first_read_and_final_reread_refuses(self):
        def edit(state, n):
            if n == 2:
                state.apply('a cooperating edit\n')
        self.fx.state.on_get = edit
        code, report, done = self.fx.run()
        self.assertEqual(code, 2, done.stdout + done.stderr)
        self.assertEqual(report['reason'], 'BODY_CHANGED_BEFORE_PATCH')
        self.assertEqual(self.fx.state.patches, 0)
        self.assertEqual(self.fx.state.body, 'a cooperating edit\n')

    def test_lease_problems_refuse_before_patch(self):
        head = self.fx.acquire()
        self.refused('ACQUIRED_HEAD', head='not-a-head')
        self.refused('LEASE_NOT_OWNED', head='0' * 40)
        self.refused('OWNER_TOKEN', head=head, owner='Bad Owner')
        self.fx.release(head)
        other = self.fx.acquire(owner='other-test-owner', execution='other-exec-01')
        self.refused('LEASE_NOT_OWNED', head=head)
        self.refused('LEASE_NOT_OWNED', head=other)

    def test_lease_check_comes_after_the_final_reread(self):
        head = self.fx.acquire()
        self.fx.release(head)
        code, report, done = self.fx.run(head=head)
        self.assertEqual((code, report['reason']), (2, 'LEASE_NOT_OWNED'))
        self.assertEqual(self.fx.state.gets, 2)

    def test_api_read_failure_refuses(self):
        self.fx.state.fail_get = {1}
        self.refused('API_READ_FAILED')
        self.fx.state.fail_get, self.fx.state.gets = {2}, 0
        self.refused('API_READ_FAILED')
        self.assertEqual(self.fx.state.gets, 2)

    def test_missing_or_wrong_token_and_bad_api_base_refuse(self):
        self.refused('TOKEN_MISSING', token=None)
        code, report, done = self.fx.run(token='wrong-token')
        self.assertEqual((code, report['reason']), (2, 'API_READ_FAILED'))
        self.assertNotIn('wrong-token', done.stdout + done.stderr)
        self.refused('API_BASE', base='http://example.com')
        self.refused('API_BASE', base='ftp://127.0.0.1')

    def test_failed_patch_is_uncertain_not_retried_and_reports_state(self):
        self.fx.state.patch_mode = 'fail'
        report = self.uncertain('PATCH_FAILED')
        self.assertEqual(report['comment']['state'], 'NOT_APPLIED')

    def test_patch_applied_but_reported_failed_is_uncertain_with_applied_state(self):
        self.fx.state.patch_mode = 'apply_then_fail'
        report = self.uncertain('PATCH_FAILED')
        self.assertEqual(report['comment']['state'], 'APPLIED')

    def test_patch_acknowledged_but_not_stored_is_a_readback_mismatch(self):
        self.fx.state.patch_mode = 'ignore'
        report = self.uncertain('READBACK_MISMATCH')
        self.assertEqual(report['comment']['state'], 'NOT_APPLIED')

    def test_normalized_newlines_are_a_readback_mismatch(self):
        self.fx.state.patch_mode = 'crlf'
        report = self.uncertain('READBACK_MISMATCH')
        self.assertEqual(report['comment']['state'], 'OTHER_CONTENT')

    def test_readback_read_failure_is_uncertain(self):
        self.fx.state.fail_get = {3}
        report = self.uncertain('READBACK_FAILED')
        self.assertEqual(report['comment']['state'], 'UNREADABLE')

    def test_verify_command_gates_before_and_after_the_write(self):
        ok = [sys.executable, '-c', 'import sys; sys.exit(0)', '{old}', '{new}']
        bad = [sys.executable, '-c', 'import sys; sys.exit(1)', '{old}', '{new}']
        self.refused('VERIFY_FAILED', verify=bad)
        code, report, done = self.fx.run(verify=ok)
        self.assertEqual(code, 0, done.stdout + done.stderr)

    def test_verify_command_failing_only_after_the_write_is_uncertain(self):
        counter = str(self.fx.root / 'count')
        flaky = [sys.executable, '-c',
                 'import sys,os; p=sys.argv[3]; n=int(open(p).read()) if os.path.exists(p) else 0; '
                 'open(p,"w").write(str(n+1)); sys.exit(0 if n == 0 else 1)', '{old}', '{new}', counter]
        report = self.uncertain('VERIFY_FAILED_AFTER_WRITE', verify=flaky)
        self.assertEqual(report['comment']['state'], 'APPLIED')

    def test_writer_source_has_no_assert_and_no_debug_guard(self):
        tree = ast.parse(WRITER.read_text(encoding='utf-8'))
        asserts = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Assert)]
        debug = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id == '__debug__']
        self.assertEqual((asserts, debug), ([], []))


if __name__ == '__main__':
    unittest.main()
