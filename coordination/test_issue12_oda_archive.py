"""Exercise the operator-actions archive offline: exact round trips and fail-closed refusals."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

if __package__:
    from . import issue12_archive_index as ai
    from . import issue12_oda_archive as oda
else:
    import issue12_archive_index as ai
    import issue12_oda_archive as oda

COMMIT = 'a' * 40
PATH1 = 'coordination/archives/index/issue-12-5999201336-oda-v001.json'
PATH2 = 'coordination/archives/index/issue-12-5999201336-oda-v002.json'
PREFIX = '<!-- issue-12-coordination-state-v1 -->\nAI disclosure: test body.\n\n```json\n'
SUFFIX = '\n```\n'


def closed(n):
    return {'status': 'CLOSED_%02d' % n, 'note': 'entrée é %d' % n, 'refs': [n, 2.5, None, True], 'deep': {'a': {'b': n}},
            'text': ('closed receipt text %d ' % n) * 20}


def active(n):
    return {'status': 'ACTIVE_%02d' % n, 'next': 'wait %d' % n}


def actions(closed_ns=(1, 2, 3), active_ns=(4, 5)):
    out = {'k-%02d' % n: closed(n) for n in closed_ns}
    out.update({'k-%02d' % n: active(n) for n in active_ns})
    return dict(sorted(out.items()))


def body(acts, extra=None):
    state = {'version': 1, 'a': {'keep': [1, 2.5, None, True]}, oda.KEY: acts, ai.KEY: [{'x': 1}], 'z': 'tail ü'}
    state.update(extra or {})
    return ai.join_body(PREFIX, state, SUFFIX)


def items_for(acts, keys):
    return [{'key': k, 'entry': acts[k]} for k in acts if k in keys]


def index_for(acts, keys, version=1, previous=None):
    return ai.index_bytes(oda.make_index(items_for(acts, keys), version, previous))


class Store:
    def __init__(self, *files):
        self.files = {(COMMIT, path): raw for path, raw in files}

    def __call__(self, commit, path):
        try:
            return self.files[(commit, path)]
        except KeyError:
            raise oda.ArchiveError('Index missing at the pinned commit and path') from None


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.acts = actions()
        self.keys = ['k-01', 'k-02', 'k-03']
        self.raw = index_for(self.acts, self.keys)
        self.store = Store((PATH1, self.raw))

    def test_round_trip_is_exact_and_smaller(self):
        original = body(self.acts)
        migrated = oda.migrate(original, self.raw, PATH1, COMMIT)
        self.assertLess(len(migrated), len(original))
        self.assertEqual(oda.resolve(migrated, self.store), original)
        state = ai.split_body(migrated)[1]
        self.assertEqual(list(state), ['version', 'a', oda.KEY, ai.KEY, 'z'])
        live = state[oda.KEY]
        self.assertEqual(list(live), [oda.MARK, 'k-01', 'k-02', 'k-03', 'k-04', 'k-05'])
        self.assertEqual(live['k-01'], {'archived': True, 'status': 'CLOSED_01'})
        self.assertEqual(live['k-04'], self.acts['k-04'])
        self.assertEqual(live[oda.MARK], oda.make_pointer(self.raw, ai.loads(self.raw.decode()), PATH1, COMMIT))

    def test_stub_keeps_status_only_when_the_entry_has_one(self):
        acts = dict(self.acts, **{'k-00': {'note': 'no status'}})
        acts = dict(sorted(acts.items()))
        raw = index_for(acts, ['k-00'])
        migrated = oda.migrate(body(acts), raw, PATH1, COMMIT)
        self.assertEqual(ai.split_body(migrated)[1][oda.KEY]['k-00'], {'archived': True})
        self.assertEqual(oda.resolve(migrated, Store((PATH1, raw))), body(acts))

    def test_unmigrated_body_resolves_to_itself(self):
        original = body(self.acts)
        self.assertEqual(oda.resolve(original, self.store), original)
        self.assertEqual(oda.resolve(original, None), original)

    def test_changed_live_entry_or_missing_key_is_refused(self):
        changed = dict(self.acts, **{'k-02': dict(closed(2), note='edited')})
        with self.assertRaisesRegex(oda.ArchiveError, 'differs from the indexed one'):
            oda.migrate(body(changed), self.raw, PATH1, COMMIT)
        fewer = {k: v for k, v in self.acts.items() if k != 'k-03'}
        with self.assertRaisesRegex(oda.ArchiveError, 'differs from the indexed one'):
            oda.migrate(body(fewer), self.raw, PATH1, COMMIT)

    def test_second_migration_with_a_first_version_is_refused(self):
        migrated = oda.migrate(body(self.acts), self.raw, PATH1, COMMIT)
        with self.assertRaisesRegex(oda.ArchiveError, 'must follow'):
            oda.migrate(migrated, self.raw, PATH1, COMMIT, self.store)

    def test_rollup_names_the_live_index_and_keeps_every_entry(self):
        migrated = oda.migrate(body(self.acts), self.raw, PATH1, COMMIT)
        more_keys = self.keys + ['k-04']
        acts = dict(self.acts, **{'k-04': closed(4)})
        previous = {'index_commit': COMMIT, 'index_path': PATH1, 'index_sha256': ai.sha256(self.raw)}
        raw2 = index_for(acts, more_keys, 2, previous)
        store = Store((PATH1, self.raw), (PATH2, raw2))
        # the live object still holds k-04 inline, now as a closed entry
        live_body = ai.join_body(PREFIX, dict(ai.split_body(migrated)[1], **{oda.KEY: dict(ai.split_body(migrated)[1][oda.KEY], **{'k-04': closed(4)})}), SUFFIX)
        rolled = oda.migrate(live_body, raw2, PATH2, COMMIT, store)
        self.assertEqual(oda.resolve(rolled, store), oda.resolve(live_body, store))
        self.assertEqual(ai.split_body(rolled)[1][oda.KEY]['k-04'], {'archived': True, 'status': 'CLOSED_04'})
        wrong = index_for(acts, more_keys, 2, dict(previous, index_sha256='b' * 64))
        with self.assertRaisesRegex(oda.ArchiveError, 'previous'):
            oda.migrate(live_body, wrong, PATH2, COMMIT, Store((PATH1, self.raw), (PATH2, wrong)))
        dropped = index_for(acts, ['k-01', 'k-04'], 2, previous)
        with self.assertRaisesRegex(oda.ArchiveError, 'keep every entry'):
            oda.migrate(live_body, dropped, PATH2, COMMIT, Store((PATH1, self.raw), (PATH2, dropped)))

    def test_index_rules(self):
        with self.assertRaisesRegex(oda.ArchiveError, 'non-empty'):
            oda.make_index([])
        with self.assertRaisesRegex(oda.ArchiveError, 'never a stub'):
            oda.make_index([{'key': 'k', 'entry': {'archived': True}}])
        with self.assertRaisesRegex(oda.ArchiveError, 'never a stub'):
            oda.make_index([{'key': oda.MARK, 'entry': closed(1)}])
        with self.assertRaisesRegex(oda.ArchiveError, 'Duplicate'):
            oda.make_index([{'key': 'k', 'entry': closed(1)}, {'key': 'k', 'entry': closed(2)}])
        with self.assertRaisesRegex(oda.ArchiveError, 'Version 1'):
            oda.make_index([{'key': 'k', 'entry': closed(1)}], 2)


class FailClosedTests(unittest.TestCase):
    def setUp(self):
        self.acts = actions()
        self.keys = ['k-01', 'k-02', 'k-03']
        self.raw = index_for(self.acts, self.keys)
        self.migrated = oda.migrate(body(self.acts), self.raw, PATH1, COMMIT)
        self.store = Store((PATH1, self.raw))

    def refused(self, text, store, pattern):
        with self.assertRaisesRegex(oda.ArchiveError, pattern):
            oda.resolve(text, store)

    def tampered(self, change):
        prefix, state, suffix = ai.split_body(self.migrated)
        change(state[oda.KEY])
        return ai.join_body(prefix, state, suffix)

    def test_missing_or_changed_index_bytes(self):
        self.refused(self.migrated, Store(), 'missing')
        self.refused(self.migrated, None, 'no source')
        self.refused(self.migrated, Store((PATH1, self.raw + b' ')), 'hash differs')

    def test_non_canonical_index_is_refused_even_with_a_matching_hash(self):
        raw = json.dumps(ai.loads(self.raw.decode()), separators=(',', ':')).encode()
        pointer = oda.make_pointer(self.raw, ai.loads(self.raw.decode()), PATH1, COMMIT)
        text = self.tampered(lambda live: live.update({oda.MARK: dict(pointer, index_sha256=ai.sha256(raw))}))
        self.refused(text, Store((PATH1, raw)), 'canonical')

    def test_pointer_must_be_first_and_well_formed(self):
        def move(live):
            pointer = live.pop(oda.MARK)
            live[oda.MARK] = pointer
        self.refused(self.tampered(move), self.store, 'first key')
        self.refused(self.tampered(lambda live: live[oda.MARK].update(entries=2)), self.store, 'count|differs')
        self.refused(self.tampered(lambda live: live[oda.MARK].update(extra=1)), self.store, 'fields differ')
        self.refused(self.tampered(lambda live: live[oda.MARK].update(index_path='coordination/x.json')), self.store, 'malformed')
        self.refused(self.tampered(lambda live: live[oda.MARK].update(keys_sha256='c' * 64)), self.store, 'key hash')

    def test_stub_must_match_the_index(self):
        self.refused(self.tampered(lambda live: live['k-01'].update(status='CLOSED_99')), self.store, 'differs from the indexed entry')
        self.refused(self.tampered(lambda live: live['k-01'].update(extra=1)), self.store, 'differs from the indexed entry')
        self.refused(self.tampered(lambda live: live.update({'k-04': {'archived': True}})), self.store, 'differ from the indexed keys')

    def test_orphan_index_entry_and_stub_without_pointer_are_refused(self):
        self.refused(self.tampered(lambda live: live.update({'k-01': closed(1)})), self.store, 'differ from the indexed keys')
        prefix, state, suffix = ai.split_body(self.migrated)
        state[oda.KEY].pop(oda.MARK)
        self.refused(ai.join_body(prefix, state, suffix), self.store, 'without a pointer')

    def test_body_without_the_key_is_refused(self):
        prefix, state, suffix = ai.split_body(self.migrated)
        state.pop(oda.KEY)
        self.refused(ai.join_body(prefix, state, suffix), self.store, 'missing')


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = oda.main([str(a) for a in argv])
        return code, out.getvalue(), err.getvalue()

    def test_build_migrate_resolve_check_against_a_real_repository(self):
        acts = actions()
        original = body(acts)
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            repo = tmp / 'repo'
            subprocess.run(['git', 'init', '-q', str(repo)], check=True)
            git = ['git', '-C', str(repo), '-c', 'user.name=t', '-c', 'user.email=t@example.test']
            (tmp / 'body.md').write_text(original, encoding='utf-8')
            code, out, err = self.run_cli('build', '--body-file', tmp / 'body.md', '--repo', repo, '--keys', 'k-01,k-02,k-03', '--out', tmp / 'index.json')
            self.assertEqual((code, err), (0, ''), out)
            index_path = repo / PATH1
            index_path.parent.mkdir(parents=True)
            index_path.write_bytes((tmp / 'index.json').read_bytes())
            subprocess.run(git + ['add', '.'], check=True)
            subprocess.run(git + ['commit', '-q', '-m', 'index'], check=True)
            commit = subprocess.run(git + ['rev-parse', 'HEAD'], check=True, capture_output=True, text=True).stdout.strip()
            code, out, err = self.run_cli('migrate', '--body-file', tmp / 'body.md', '--repo', repo, '--index-file', tmp / 'index.json',
                                          '--index-path', PATH1, '--commit', commit, '--out', tmp / 'after.md')
            self.assertEqual((code, err), (0, ''))
            self.assertGreater(json.loads(out)['saved_chars'], 0)
            code, out, err = self.run_cli('resolve', '--body-file', tmp / 'after.md', '--repo', repo, '--out', tmp / 'back.md')
            self.assertEqual(code, 0, err)
            self.assertEqual((tmp / 'back.md').read_text(encoding='utf-8'), original)
            code, out, err = self.run_cli('check', '--body-file', tmp / 'after.md', '--repo', repo, '--ancestor-of', 'HEAD')
            self.assertEqual(json.loads(out), {'pointer': True, 'entries': 5, 'archived': 3, 'inline': 2})
            tree = subprocess.run(git + ['hash-object', '-t', 'tree', '-w', '/dev/null'], check=True, capture_output=True, text=True).stdout.strip()
            other = subprocess.run(git + ['commit-tree', tree, '-m', 'unrelated'], check=True, capture_output=True, text=True).stdout.strip()
            code, out, err = self.run_cli('check', '--body-file', tmp / 'after.md', '--repo', repo, '--ancestor-of', other)
            self.assertEqual(code, 1)
            self.assertIn('not reachable', err)

    def test_file_bytes_are_verified_and_written_without_newline_translation(self):
        acts = actions()
        original = body(acts).replace('AI disclosure: test body.\n\n', 'AI disclosure: test body.\r\n\r\n')
        self.assertIn('\r\n', original)
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            repo = tmp / 'repo'
            subprocess.run(['git', 'init', '-q', str(repo)], check=True)
            git = ['git', '-C', str(repo), '-c', 'user.name=t', '-c', 'user.email=t@example.test']
            (repo / PATH1).parent.mkdir(parents=True)
            (repo / PATH1).write_bytes(index_for(acts, ['k-01', 'k-02', 'k-03']))
            subprocess.run(git + ['add', '.'], check=True)
            subprocess.run(git + ['commit', '-q', '-m', 'index'], check=True)
            commit = subprocess.run(git + ['rev-parse', 'HEAD'], check=True, capture_output=True, text=True).stdout.strip()
            (tmp / 'body.md').write_bytes(original.encode('utf-8'))
            code, out, err = self.run_cli('migrate', '--body-file', tmp / 'body.md', '--repo', repo, '--index-file', repo / PATH1,
                                          '--index-path', PATH1, '--commit', commit, '--out', tmp / 'after.md')
            self.assertEqual((code, err), (0, ''))
            report = json.loads(out)
            self.assertEqual(report['before_sha256'], ai.sha256((tmp / 'body.md').read_bytes()))
            self.assertEqual(report['after_sha256'], ai.sha256((tmp / 'after.md').read_bytes()))
            self.assertIn(b'\r\n', (tmp / 'after.md').read_bytes())
            code, out, err = self.run_cli('resolve', '--body-file', tmp / 'after.md', '--repo', repo, '--out', tmp / 'back.md')
            self.assertEqual((code, err), (0, ''))
            self.assertEqual((tmp / 'back.md').read_bytes(), original.encode('utf-8'))
            self.assertEqual(json.loads(out)['sha256'], ai.sha256(original))

    def test_body_file_that_is_not_utf8_is_refused_without_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / 'body.md').write_bytes(body(actions()).encode('utf-8') + b'\xff')
            (tmp / 'index.json').write_bytes(index_for(actions(), ['k-01']))
            code, out, err = self.run_cli('migrate', '--body-file', tmp / 'body.md', '--repo', tmp, '--index-file', tmp / 'index.json',
                                          '--index-path', PATH1, '--commit', COMMIT, '--out', tmp / 'after.md')
            self.assertEqual(code, 1)
            self.assertIn('REFUSED', err)
            self.assertFalse((tmp / 'after.md').exists())

    def test_refusal_writes_no_output(self):
        acts = actions()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            raw = index_for(acts, ['k-01'])
            (tmp / 'body.md').write_text(body(dict(acts, **{'k-01': dict(closed(1), note='edited')})), encoding='utf-8')
            (tmp / 'index.json').write_bytes(raw)
            code, out, err = self.run_cli('migrate', '--body-file', tmp / 'body.md', '--repo', tmp, '--index-file', tmp / 'index.json',
                                          '--index-path', PATH1, '--commit', COMMIT, '--out', tmp / 'after.md')
            self.assertEqual(code, 1)
            self.assertIn('REFUSED', err)
            self.assertFalse((tmp / 'after.md').exists())

    def test_build_refuses_unknown_or_misordered_keys(self):
        acts = actions()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / 'body.md').write_text(body(acts), encoding='utf-8')
            for keys in ('k-01,nope', 'k-02,k-01'):
                code, out, err = self.run_cli('build', '--body-file', tmp / 'body.md', '--repo', tmp, '--keys', keys, '--out', tmp / 'i.json')
                self.assertEqual(code, 1)
                self.assertFalse((tmp / 'i.json').exists())


if __name__ == '__main__':
    unittest.main()
