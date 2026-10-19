#!/usr/bin/env python3
"""Hash-pinned index of the archive references in issue-12 comment 5999201336.

Moves the leading run of `continuation_receipt_archives` entries into an immutable
repository file and back, byte for byte. Offline: reads git objects with `git show` only.
It posts nothing and is not a cursor, scheduler or ledger."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

FORMAT = 'issue12-archive-pointer-index-v1'
SOURCE_URL = 'https://github.com/scottonchain/microcredit-agent-testbed/issues/12#issuecomment-5999201336'
KEY = 'continuation_receipt_archives'
POINTER_KEYS = ('index_commit', 'index_path', 'index_sha256', 'entries', 'last_snapshot_sha256')
PREVIOUS_KEYS = ('index_commit', 'index_path', 'index_sha256')
PATH = re.compile(r'coordination/archives/index/issue-12-5999201336-v([0-9]{3})\.json')
HEX40 = re.compile(r'[0-9a-f]{40}')
HEX64 = re.compile(r'[0-9a-f]{64}')
FENCE = re.compile(r'```json\n(.*?)\n```', re.S)
LIMIT = 65536


class ArchiveIndexError(RuntimeError):
    pass


def sha256(data):
    return hashlib.sha256(data.encode('utf-8') if isinstance(data, str) else data).hexdigest()


def _pairs(pairs):
    keys = [key for key, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ArchiveIndexError('Duplicate JSON key')
    return dict(pairs)


def _constant(name):
    raise ArchiveIndexError('Non-standard JSON value ' + name)


def loads(text):
    try:
        return json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant)
    except ValueError as error:
        raise ArchiveIndexError('Invalid JSON: ' + str(error)) from error


def compact(value):
    return json.dumps(value, separators=(',', ':'), ensure_ascii=False)


def split_body(body):
    """Return prefix, decoded state and suffix of the single compact JSON fence."""
    match = FENCE.search(body)
    if body.count('```') != 2 or not match:
        raise ArchiveIndexError('Expected exactly one json fence')
    state = loads(match.group(1))
    if not isinstance(state, dict) or compact(state) != match.group(1):
        raise ArchiveIndexError('State is not the canonical compact encoding')
    return body[:match.start(1)], state, body[match.end(1):]


def join_body(prefix, state, suffix):
    return prefix + compact(state) + suffix


def is_pointer(entry):
    return isinstance(entry, dict) and 'index_path' in entry


def index_bytes(index):
    return (json.dumps(index, indent=2, ensure_ascii=False) + '\n').encode('utf-8')


def make_index(entries, version=1, previous=None):
    if not isinstance(entries, list) or not entries or not all(isinstance(e, dict) for e in entries):
        raise ArchiveIndexError('Entries must be a non-empty list of objects')
    if any(is_pointer(e) for e in entries):
        raise ArchiveIndexError('An index never contains a pointer')
    if not all(HEX64.fullmatch(str(e.get('body_utf8_sha256'))) for e in entries):
        raise ArchiveIndexError('Every entry names its snapshot hash')
    if (version == 1) != (previous is None):
        raise ArchiveIndexError('Version 1 has no previous index; every later version names one')
    return {'format': FORMAT, 'source_url': SOURCE_URL, 'version': version, 'previous': previous,
            'entry_count': len(entries), 'entries_sha256': sha256(compact(entries)), 'entries': entries}


def make_pointer(raw, index, path, commit):
    if not PATH.fullmatch(path) or int(PATH.fullmatch(path).group(1)) != index['version']:
        raise ArchiveIndexError('Index path must be the numbered file for its version')
    if not HEX40.fullmatch(commit):
        raise ArchiveIndexError('Commit must be a full lowercase SHA-1')
    return {'index_commit': commit, 'index_path': path, 'index_sha256': sha256(raw),
            'entries': index['entry_count'], 'last_snapshot_sha256': index['entries'][-1]['body_utf8_sha256']}


def check_pointer(pointer):
    if not isinstance(pointer, dict) or set(pointer) != set(POINTER_KEYS):
        raise ArchiveIndexError('Pointer fields differ from the format')
    if not (HEX40.fullmatch(str(pointer['index_commit'])) and HEX64.fullmatch(str(pointer['index_sha256']))
            and HEX64.fullmatch(str(pointer['last_snapshot_sha256'])) and PATH.fullmatch(str(pointer['index_path']))
            and type(pointer['entries']) is int and pointer['entries'] > 0):
        raise ArchiveIndexError('Pointer value is malformed')


def check_index(raw, pointer):
    """Fail closed unless the fetched bytes are exactly the index the pointer pins."""
    check_pointer(pointer)
    if sha256(raw) != pointer['index_sha256']:
        raise ArchiveIndexError('Index hash differs from the pointer')
    try:
        index = loads(raw.decode('utf-8'))
    except UnicodeDecodeError as error:
        raise ArchiveIndexError('Index is not UTF-8') from error
    if not isinstance(index, dict) or index_bytes(index) != raw:
        raise ArchiveIndexError('Index is not the canonical serialization')
    entries = index.get('entries')
    if index.get('format') != FORMAT or index.get('source_url') != SOURCE_URL:
        raise ArchiveIndexError('Index format or source differs')
    if type(index.get('version')) is not int or int(PATH.fullmatch(pointer['index_path']).group(1)) != index['version']:
        raise ArchiveIndexError('Index version differs from its path')
    previous = index.get('previous')
    if index['version'] == 1:
        if previous is not None:
            raise ArchiveIndexError('Version 1 names a previous index')
    elif not isinstance(previous, dict) or set(previous) != set(PREVIOUS_KEYS):
        raise ArchiveIndexError('Later versions must name the previous index')
    if make_index(entries, index['version'], previous) != index:
        raise ArchiveIndexError('Index counts or entry hash differ')
    if index['entry_count'] != pointer['entries'] or entries[-1]['body_utf8_sha256'] != pointer['last_snapshot_sha256']:
        raise ArchiveIndexError('Pointer count or last snapshot differs from the index')
    return index


def git_fetch(repo):
    def fetch(commit, path):
        result = subprocess.run(['git', '-C', str(repo), 'show', commit + ':' + path], capture_output=True)
        if result.returncode:
            raise ArchiveIndexError('Index missing at the pinned commit and path')
        return result.stdout
    return fetch


def expand(archives, fetch):
    """Return the full entry list and, when present, the leading pointer with its index."""
    if not isinstance(archives, list):
        raise ArchiveIndexError(KEY + ' is not a list')
    places = [i for i, entry in enumerate(archives) if is_pointer(entry)]
    if not places:
        return archives, None, None
    if places != [0]:
        raise ArchiveIndexError('A pointer is valid only once, as the first element')
    pointer = archives[0]
    check_pointer(pointer)
    if fetch is None:
        raise ArchiveIndexError('The list starts with a pointer and no source for the index was given')
    index = check_index(fetch(pointer['index_commit'], pointer['index_path']), pointer)
    return index['entries'] + archives[1:], pointer, index


def resolve(body, fetch):
    """Rebuild the body as it was before any indexed entries were replaced."""
    prefix, state, suffix = split_body(body)
    state[KEY], pointer, _ = expand(state[KEY], fetch)
    return join_body(prefix, state, suffix) if pointer else body


def migrate(body, raw, path, commit, fetch=None):
    """Replace the leading run of entries named by the index with one pointer.

    Returns nothing unless the result expands to exactly what the input expands to. For the
    first migration the input has no pointer, so that is byte equality with the input body;
    for a roll-up both sides are compared fully expanded, since the input still holds the
    older pointer."""
    prefix, state, suffix = split_body(body)
    index = loads(raw.decode('utf-8'))
    pointer = make_pointer(raw, index, path, commit)
    check_index(raw, pointer)
    full, old, old_index = expand(state[KEY], fetch)
    count = index['entry_count']
    if full[:count] != index['entries'] or compact(full[:count]) != compact(index['entries']):
        raise ArchiveIndexError('The live list differs inside the indexed entries; rebuild and re-review, never overwrite')
    if old is None:
        if index['version'] != 1:
            raise ArchiveIndexError('The first index must be version 1')
    else:
        if index['version'] != old_index['version'] + 1 or count < old_index['entry_count']:
            raise ArchiveIndexError('A later version must follow the live one and keep every entry')
        if index['previous'] != {k: old[k] for k in PREVIOUS_KEYS}:
            raise ArchiveIndexError('The index does not name the live index as previous')
    state[KEY] = [pointer] + full[count:]
    after = join_body(prefix, state, suffix)
    served = lambda c, p: raw if p == path else fetch(c, p)
    if resolve(after, served) != resolve(body, served):
        raise ArchiveIndexError('Round trip differs from the original body')
    return after


def report(before, after, expanded):
    return {'before_chars': len(before), 'after_chars': len(after), 'saved_chars': len(before) - len(after),
            'headroom_after': LIMIT - len(after), 'before_sha256': sha256(before), 'after_sha256': sha256(after),
            'expanded_sha256': sha256(expanded)}


def read_body(args):
    text = Path(args.body_file).read_text(encoding='utf-8')
    return loads(text)['body'] if args.comment_json else text


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('build', 'migrate', 'resolve', 'check'):
        step = sub.add_parser(name)
        step.add_argument('--body-file', required=True)
        step.add_argument('--comment-json', action='store_true', help='body-file is the GitHub API comment JSON')
        step.add_argument('--repo', default='.')
    sub.choices['build'].add_argument('--count', type=int, required=True)
    sub.choices['build'].add_argument('--version', type=int, default=1)
    sub.choices['build'].add_argument('--previous-json')
    sub.choices['build'].add_argument('--out', required=True)
    sub.choices['migrate'].add_argument('--index-file', required=True)
    sub.choices['migrate'].add_argument('--index-path', required=True)
    sub.choices['migrate'].add_argument('--commit', required=True)
    sub.choices['migrate'].add_argument('--out', required=True)
    sub.choices['resolve'].add_argument('--out', required=True)
    sub.choices['check'].add_argument('--ancestor-of', help='require the pinned commit to be reachable from this ref')
    args = parser.parse_args(argv)
    body, fetch = read_body(args), git_fetch(args.repo)
    try:
        if args.command == 'build':
            _, state, _ = split_body(body)
            full, _, _ = expand(state[KEY], fetch)
            previous = loads(args.previous_json) if args.previous_json else None
            Path(args.out).write_bytes(index_bytes(make_index(full[:args.count], args.version, previous)))
            print(json.dumps({'index_sha256': sha256(Path(args.out).read_bytes()), 'entries': args.count}))
        elif args.command == 'migrate':
            raw = Path(args.index_file).read_bytes()
            after = migrate(body, raw, args.index_path, args.commit, fetch)
            expanded = resolve(after, lambda commit, path: raw if path == args.index_path else fetch(commit, path))
            Path(args.out).write_text(after, encoding='utf-8')
            print(json.dumps(report(body, after, expanded)))
        elif args.command == 'resolve':
            Path(args.out).write_text(resolve(body, fetch), encoding='utf-8')
            print(json.dumps({'sha256': sha256(Path(args.out).read_bytes())}))
        else:
            _, state, _ = split_body(body)
            full, pointer, index = expand(state[KEY], fetch)
            if pointer and args.ancestor_of and subprocess.run(
                    ['git', '-C', args.repo, 'merge-base', '--is-ancestor', pointer['index_commit'], args.ancestor_of]).returncode:
                raise ArchiveIndexError('Pinned commit is not reachable from ' + args.ancestor_of)
            print(json.dumps({'pointer': bool(pointer), 'entries': len(full), 'inline': len(full) - (index['entry_count'] if index else 0)}))
    except ArchiveIndexError as error:
        print('REFUSED: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
