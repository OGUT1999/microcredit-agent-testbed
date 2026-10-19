"""Exercise the archive pointer index offline: exact round trips and fail-closed refusals."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

if __package__:
    from . import issue12_archive_index as ai
else:
    import issue12_archive_index as ai

ROOT = Path(__file__).resolve().parent.parent
COMMIT = 'a' * 40
PATH1 = 'coordination/archives/index/issue-12-5999201336-v001.json'
PATH2 = 'coordination/archives/index/issue-12-5999201336-v002.json'
PREFIX = '<!-- issue-12-coordination-state-v1 -->\nAI disclosure: test body.\n\n```json\n'
SUFFIX = '\n```\n'


def entry(n):
    return {'commit': format(n, 'x') * 40, 'path': 'coordination/archives/issue-12-5999201336-%02d.json' % n,
            'source_url': ai.SOURCE_URL, 'source_updated_at': '2026-10-19T00:%02d:00Z' % n,
            'body_utf8_sha256': format(n, 'x') * 64, 'receipt_keys': ['receipt-é-%02d' % n], 'review_url': 'https://example.test/%d' % n}


def body(entries, extra=None):
    state = {'version': 1, 'a': {'keep': [1, 2.5, None, True]}, ai.KEY: entries, 'z': 'tail ü'}
    state.update(extra or {})
    return ai.join_body(PREFIX, state, SUFFIX)


class Store:
    def __init__(self, *files):
        self.files = {(COMMIT, path): raw for path, raw in files}

    def __call__(self, commit, path):
        try:
            return self.files[(commit, path)]
        except KeyError:
            raise ai.ArchiveIndexError('Index missing at the pinned commit and path') from None


def index_for(entries, version=1, previous=None):
    return ai.index_bytes(ai.make_index(entries, version, previous))


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.entries = [entry(n) for n in range(1, 6)]
        self.raw = index_for(self.entries)
        self.store = Store((PATH1, self.raw))

    def test_round_trip_is_exact_and_smaller(self):
        original = body(self.entries)
        migrated = ai.migrate(original, self.raw, PATH1, COMMIT)
        self.assertLess(len(migrated), len(original))
        self.assertEqual(ai.resolve(migrated, self.store), original)
        state = ai.split_body(migrated)[1]
        self.assertEqual(list(state), ['version', 'a', ai.KEY, 'z'])
        self.assertEqual(state[ai.KEY], [ai.make_pointer(self.raw, ai.loads(self.raw.decode()), PATH1, COMMIT)])

    def test_newer_entries_stay_inline_and_every_other_byte_is_kept(self):
        original = body(self.entries + [entry(6), entry(7)])
        migrated = ai.migrate(original, self.raw, PATH1, COMMIT)
        archives = ai.split_body(migrated)[1][ai.KEY]
        self.assertEqual(archives[1:], [entry(6), entry(7)])
        self.assertEqual(ai.resolve(migrated, self.store), original)
        self.assertEqual(ai.resolve(original, self.store), original)

    def test_changed_entry_inside_the_indexed_run_is_refused(self):
        changed = self.entries[:2] + [dict(entry(3), review_url='https://example.test/other')] + self.entries[3:]
        with self.assertRaisesRegex(ai.ArchiveIndexError, 'differs inside'):
            ai.migrate(body(changed), self.raw, PATH1, COMMIT)
        with self.assertRaisesRegex(ai.ArchiveIndexError, 'differs inside'):
            ai.migrate(body(self.entries[:4]), self.raw, PATH1, COMMIT)

    def test_second_migration_with_a_first_version_is_refused(self):
        migrated = ai.migrate(body(self.entries), self.raw, PATH1, COMMIT)
        with self.assertRaisesRegex(ai.ArchiveIndexError, 'must follow'):
            ai.migrate(migrated, self.raw, PATH1, COMMIT, self.store)

    def test_rollup_names_the_live_index_and_keeps_every_entry(self):
        more = self.entries + [entry(6), entry(7), entry(8)]
        migrated = ai.migrate(body(more), self.raw, PATH1, COMMIT)
        previous = {'index_commit': COMMIT, 'index_path': PATH1, 'index_sha256': ai.sha256(self.raw)}
        raw2 = index_for(more, 2, previous)
        store = Store((PATH1, self.raw), (PATH2, raw2))
        rolled = ai.migrate(migrated, raw2, PATH2, COMMIT, store)
        self.assertEqual(len(ai.split_body(rolled)[1][ai.KEY]), 1)
        self.assertEqual(ai.resolve(rolled, store), body(more))
        wrong = index_for(more, 2, dict(previous, index_sha256='b' * 64))
        with self.assertRaisesRegex(ai.ArchiveIndexError, 'previous'):
            ai.migrate(migrated, wrong, PATH2, COMMIT, Store((PATH1, self.raw), (PATH2, wrong)))
        shorter = index_for(self.entries[:3] + more[5:], 2, previous)
        with self.assertRaisesRegex(ai.ArchiveIndexError, 'differs inside'):
            ai.migrate(migrated, shorter, PATH2, COMMIT, Store((PATH1, self.raw), (PATH2, shorter)))


class FailClosedTests(unittest.TestCase):
    def setUp(self):
        self.entries = [entry(n) for n in range(1, 4)]
        self.raw = index_for(self.entries)
        self.migrated = ai.migrate(body(self.entries), self.raw, PATH1, COMMIT)

    def refused(self, text, store, pattern):
        with self.assertRaisesRegex(ai.ArchiveIndexError, pattern):
            ai.resolve(text, store)

    def test_missing_index(self):
        self.refused(self.migrated, Store(), 'missing')

    def test_tampered_index_bytes(self):
        self.refused(self.migrated, Store((PATH1, self.raw.replace(b'2026-10-19T00:01', b'2026-10-19T00:09'))), 'hash differs')
        self.refused(self.migrated, Store((PATH1, self.raw + b'\n')), 'hash differs')

    def test_index_that_is_not_the_canonical_serialization(self):
        loose = json.dumps(json.loads(self.raw), separators=(',', ':')).encode()
        pointer = ai.make_pointer(self.raw, json.loads(self.raw), PATH1, COMMIT)
        text = ai.migrate(body(self.entries), self.raw, PATH1, COMMIT).replace(pointer['index_sha256'], ai.sha256(loose))
        self.refused(text, Store((PATH1, loose)), 'canonical')

    def test_pointer_disagreeing_with_the_index(self):
        state = ai.split_body(self.migrated)[1]
        for field, value in (('entries', 2), ('last_snapshot_sha256', 'c' * 64)):
            state[ai.KEY][0][field] = value
            self.refused(ai.join_body(PREFIX, state, SUFFIX), Store((PATH1, self.raw)), 'differs from the index')
            state = ai.split_body(self.migrated)[1]

    def test_malformed_or_misplaced_pointers(self):
        state = ai.split_body(self.migrated)[1]
        pointer = state[ai.KEY][0]
        cases = [dict(pointer, extra=1), {k: v for k, v in pointer.items() if k != 'entries'}, dict(pointer, index_commit='A' * 40),
                 dict(pointer, entries=True), dict(pointer, index_path='coordination/archives/index/other.json')]
        for case in cases:
            state[ai.KEY] = [case]
            self.refused(ai.join_body(PREFIX, state, SUFFIX), Store((PATH1, self.raw)), 'Pointer')
        state[ai.KEY] = [entry(9), pointer]
        self.refused(ai.join_body(PREFIX, state, SUFFIX), Store((PATH1, self.raw)), 'first element')
        state[ai.KEY] = [pointer, pointer]
        self.refused(ai.join_body(PREFIX, state, SUFFIX), Store((PATH1, self.raw)), 'first element')

    def test_body_that_is_not_one_canonical_json_fence(self):
        good = body(self.entries)
        for bad, pattern in ((good.replace('"version":1', '"version":1,"version":2'), 'Duplicate'),
                             (good.replace('"version":1', '"version":NaN'), 'Non-standard'),
                             (good.replace('"version":1,', '"version": 1,'), 'canonical'),
                             (good + good, 'exactly one'), ('no fence', 'exactly one')):
            with self.assertRaisesRegex(ai.ArchiveIndexError, pattern):
                ai.split_body(bad)

    def test_index_never_holds_a_pointer_or_a_missing_hash(self):
        for entries in ([], [{'index_path': 'x'}], [{'path': 'p'}], 'text'):
            with self.assertRaises(ai.ArchiveIndexError):
                ai.make_index(entries)
        with self.assertRaises(ai.ArchiveIndexError):
            ai.make_index(self.entries, 1, {'index_commit': COMMIT})
        with self.assertRaises(ai.ArchiveIndexError):
            ai.make_index(self.entries, 2, None)

    def test_pointer_construction_checks_path_and_commit(self):
        index = json.loads(self.raw)
        for path, commit in ((PATH2, COMMIT), ('coordination/archives/x.json', COMMIT), (PATH1, 'abc')):
            with self.assertRaises(ai.ArchiveIndexError):
                ai.make_pointer(self.raw, index, path, commit)


class GitBackedTests(unittest.TestCase):
    def test_command_line_round_trip_against_a_real_commit(self):
        entries = [entry(n) for n in range(1, 5)]
        raw = index_for(entries)
        with tempfile.TemporaryDirectory() as tmp:
            repo, work = Path(tmp) / 'repo', Path(tmp)
            git = lambda *a: subprocess.run(['git', '-C', str(repo), *a], check=True, capture_output=True, text=True).stdout.strip()
            subprocess.run(['git', 'init', '-q', str(repo)], check=True)
            (repo / PATH1).parent.mkdir(parents=True)
            (repo / PATH1).write_bytes(raw)
            git('add', '.')
            git('-c', 'user.name=T', '-c', 'user.email=t@example.test', 'commit', '-q', '-m', 'index')
            commit = git('rev-parse', 'HEAD')
            original = body(entries + [entry(5)])
            (work / 'body.txt').write_text(original, encoding='utf-8')
            run = lambda *a: self.run_main(list(a))
            self.assertEqual(run('migrate', '--body-file', str(work / 'body.txt'), '--repo', str(repo), '--index-file', str(repo / PATH1),
                                 '--index-path', PATH1, '--commit', commit, '--out', str(work / 'migrated.txt')), 0)
            for command, out in (('resolve', ['--out', str(work / 'back.txt')]), ('check', ['--ancestor-of', 'HEAD'])):
                self.assertEqual(run(command, '--body-file', str(work / 'migrated.txt'), '--repo', str(repo), *out), 0)
            self.assertEqual((work / 'back.txt').read_text(encoding='utf-8'), original)
            # A later commit that changes the file does not change what the pinned commit holds, but a pointer to it fails.
            (repo / PATH1).write_bytes(raw + b' ')
            git('-c', 'user.name=T', '-c', 'user.email=t@example.test', 'commit', '-q', '-am', 'tamper')
            migrated = (work / 'migrated.txt').read_text(encoding='utf-8')
            self.assertEqual(run('check', '--body-file', str(work / 'migrated.txt'), '--repo', str(repo)), 0)
            (work / 'tampered.txt').write_text(migrated.replace(commit, git('rev-parse', 'HEAD')), encoding='utf-8')
            self.assertEqual(run('check', '--body-file', str(work / 'tampered.txt'), '--repo', str(repo)), 1)
            # A pinned commit that is not reachable from the required ref is refused.
            git('checkout', '-q', '--orphan', 'other')
            git('-c', 'user.name=T', '-c', 'user.email=t@example.test', 'commit', '-q', '--allow-empty', '-m', 'other')
            self.assertEqual(run('check', '--body-file', str(work / 'migrated.txt'), '--repo', str(repo), '--ancestor-of', 'other'), 1)

    def test_command_line_rollup_matches_expanded_forms_and_refusals_write_nothing(self):
        entries = [entry(n) for n in range(1, 5)]
        raw1 = index_for(entries[:3])
        with tempfile.TemporaryDirectory() as tmp:
            repo, work = Path(tmp) / 'repo', Path(tmp)
            git = lambda *a: subprocess.run(['git', '-C', str(repo), *a], check=True, capture_output=True, text=True).stdout.strip()
            commit_as = lambda message: git('-c', 'user.name=T', '-c', 'user.email=t@example.test', 'commit', '-q', '-m', message)
            subprocess.run(['git', 'init', '-q', str(repo)], check=True)
            (repo / PATH1).parent.mkdir(parents=True)
            (repo / PATH1).write_bytes(raw1)
            git('add', '.')
            commit_as('v001')
            commit1 = git('rev-parse', 'HEAD')
            original = body(entries)
            (work / 'body.txt').write_text(original, encoding='utf-8')
            run = lambda *a: self.run_main(list(a))
            migrate = lambda src, index, path, commit, out: run(
                'migrate', '--body-file', str(src), '--repo', str(repo), '--index-file', str(index), '--index-path', path,
                '--commit', commit, '--out', str(out))
            self.assertEqual(migrate(work / 'body.txt', repo / PATH1, PATH1, commit1, work / 'first.txt'), 0)
            first = (work / 'first.txt').read_text(encoding='utf-8')
            self.assertEqual(ai.split_body(first)[1][ai.KEY][1:], [entries[3]])
            # Version 2 holds every entry and names version 1; the input body still holds the version 1 pointer.
            previous = {'index_commit': commit1, 'index_path': PATH1, 'index_sha256': ai.sha256(raw1)}
            raw2 = index_for(entries, 2, previous)
            (repo / PATH2).write_bytes(raw2)
            git('add', '.')
            commit_as('v002')
            commit2 = git('rev-parse', 'HEAD')
            self.assertEqual(migrate(work / 'first.txt', repo / PATH2, PATH2, commit2, work / 'second.txt'), 0)
            second = (work / 'second.txt').read_text(encoding='utf-8')
            archives = ai.split_body(second)[1][ai.KEY]
            self.assertEqual((len(archives), archives[0]['index_path'], archives[0]['entries']), (1, PATH2, 4))
            fetch = ai.git_fetch(repo)
            self.assertEqual(ai.resolve(second, fetch), original)
            self.assertEqual(ai.resolve(second, fetch), ai.resolve(first, fetch))
            self.assertEqual(run('check', '--body-file', str(work / 'second.txt'), '--repo', str(repo), '--ancestor-of', 'HEAD'), 0)
            # Refusals leave no candidate behind: wrong previous, a changed entry inside the indexed run, no live pointer source.
            wrong = index_for(entries, 2, dict(previous, index_sha256='b' * 64))
            (work / 'wrong.json').write_bytes(wrong)
            changed = body(entries[:2] + [dict(entries[2], review_url='https://example.test/x')] + entries[3:])
            (work / 'changed.txt').write_text(changed, encoding='utf-8')
            for src, index, path, out in ((work / 'first.txt', work / 'wrong.json', PATH2, 'refused-a.txt'),
                                          (work / 'changed.txt', repo / PATH1, PATH1, 'refused-b.txt'),
                                          (work / 'first.txt', repo / PATH1, PATH1, 'refused-c.txt')):
                self.assertEqual(migrate(src, index, path, commit2, work / out), 1)
                self.assertFalse((work / out).exists())

    def test_command_line_keeps_the_line_endings_of_the_body_file(self):
        entries = [entry(n) for n in range(1, 5)]
        raw = index_for(entries)
        original = body(entries + [entry(5)]).replace('\n\n```json', '\r\n\r\n```json')
        self.assertIn('\r\n', original)
        with tempfile.TemporaryDirectory() as tmp:
            repo, work = Path(tmp) / 'repo', Path(tmp)
            git = lambda *a: subprocess.run(['git', '-C', str(repo), *a], check=True, capture_output=True, text=True).stdout.strip()
            subprocess.run(['git', 'init', '-q', str(repo)], check=True)
            (repo / PATH1).parent.mkdir(parents=True)
            (repo / PATH1).write_bytes(raw)
            git('add', '.')
            git('-c', 'user.name=T', '-c', 'user.email=t@example.test', 'commit', '-q', '-m', 'index')
            commit = git('rev-parse', 'HEAD')
            (work / 'body.txt').write_bytes(original.encode('utf-8'))
            run = lambda *a: self.run_main(list(a))
            self.assertEqual(run('migrate', '--body-file', str(work / 'body.txt'), '--repo', str(repo), '--index-file', str(repo / PATH1),
                                 '--index-path', PATH1, '--commit', commit, '--out', str(work / 'migrated.txt')), 0)
            self.assertIn(b'\r\n', (work / 'migrated.txt').read_bytes())
            self.assertEqual(run('resolve', '--body-file', str(work / 'migrated.txt'), '--repo', str(repo), '--out', str(work / 'back.txt')), 0)
            self.assertEqual((work / 'back.txt').read_bytes(), original.encode('utf-8'))

    @staticmethod
    def run_main(argv):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return ai.main(argv)


class CommittedIndexTests(unittest.TestCase):
    def test_each_committed_index_is_canonical_and_matches_its_snapshots(self):
        paths = sorted((ROOT / 'coordination/archives/index').glob('issue-12-5999201336-v*.json'))
        self.assertTrue(paths)
        for number, path in enumerate(paths, 1):
            raw = path.read_bytes()
            self.assertEqual(path.relative_to(ROOT).as_posix(), 'coordination/archives/index/issue-12-5999201336-v%03d.json' % number)
            index = ai.check_index(raw, ai.make_pointer(raw, ai.loads(raw.decode()), path.relative_to(ROOT).as_posix(), COMMIT))
            self.assertEqual(index['version'], number)
            for item in index['entries']:
                snapshot = json.loads((ROOT / item['path']).read_text(encoding='utf-8'))
                self.assertEqual(snapshot['format'], 'immutable-canonical-comment-snapshot-v1')
                self.assertEqual(ai.sha256(snapshot['body']), item['body_utf8_sha256'])
                self.assertEqual(snapshot['body_utf8_sha256'], item['body_utf8_sha256'])
                self.assertEqual(snapshot['source_updated_at'], item['source_updated_at'])
                self.assertEqual(snapshot['source_url'], item['source_url'])


if __name__ == '__main__':
    unittest.main()
