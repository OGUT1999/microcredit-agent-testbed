#!/usr/bin/env python3
"""Hash-pinned archive of closed `operator_directed_actions` entries of issue-12 comment 5999201336.

Moves chosen entries of that object into an immutable repository file and back, byte for
byte, leaving a small stub under each original key and one pointer. Offline: reads git
objects with `git show` only. It posts nothing and is not a cursor, scheduler or ledger.
It reuses the helpers of `issue12_archive_index.py` and leaves that tool's list untouched."""
import argparse
import json
from pathlib import Path
import re
import sys

if __package__:
    from . import issue12_archive_index as ai
else:
    import issue12_archive_index as ai

FORMAT = 'issue12-oda-archive-index-v1'
KEY = 'operator_directed_actions'
MARK = '_archive'
POINTER_KEYS = ('index_commit', 'index_path', 'index_sha256', 'entries', 'keys_sha256')
PREVIOUS_KEYS = ('index_commit', 'index_path', 'index_sha256')
PATH = re.compile(r'coordination/archives/index/issue-12-5999201336-oda-v([0-9]{3})\.json')
ArchiveError = ai.ArchiveIndexError


def is_stub(value):
    return isinstance(value, dict) and value.get('archived') is True


def stub_for(entry):
    stub = {'archived': True}
    if 'status' in entry:
        stub['status'] = entry['status']
    return stub


def make_index(items, version=1, previous=None):
    """`items` is a non-empty list of {'key': str, 'entry': object} in live order."""
    if not isinstance(items, list) or not items:
        raise ArchiveError('Items must be a non-empty list')
    for item in items:
        if not isinstance(item, dict) or set(item) != {'key', 'entry'} or not isinstance(item['key'], str) \
                or item['key'] == MARK or not isinstance(item['entry'], dict) or is_stub(item['entry']):
            raise ArchiveError('Every item is a key and a full entry, never a stub or the pointer key')
    keys = [item['key'] for item in items]
    if len(keys) != len(set(keys)):
        raise ArchiveError('Duplicate key in the index')
    if (version == 1) != (previous is None):
        raise ArchiveError('Version 1 has no previous index; every later version names one')
    return {'format': FORMAT, 'source_url': ai.SOURCE_URL, 'version': version, 'previous': previous,
            'entry_count': len(items), 'entries_sha256': ai.sha256(ai.compact(items)), 'entries': items}


def make_pointer(raw, index, path, commit):
    if not PATH.fullmatch(path) or int(PATH.fullmatch(path).group(1)) != index['version']:
        raise ArchiveError('Index path must be the numbered file for its version')
    if not ai.HEX40.fullmatch(commit):
        raise ArchiveError('Commit must be a full lowercase SHA-1')
    return {'index_commit': commit, 'index_path': path, 'index_sha256': ai.sha256(raw), 'entries': index['entry_count'],
            'keys_sha256': ai.sha256(ai.compact([item['key'] for item in index['entries']]))}


def check_pointer(pointer):
    if not isinstance(pointer, dict) or set(pointer) != set(POINTER_KEYS):
        raise ArchiveError('Pointer fields differ from the format')
    if not (ai.HEX40.fullmatch(str(pointer['index_commit'])) and ai.HEX64.fullmatch(str(pointer['index_sha256']))
            and ai.HEX64.fullmatch(str(pointer['keys_sha256'])) and PATH.fullmatch(str(pointer['index_path']))
            and type(pointer['entries']) is int and pointer['entries'] > 0):
        raise ArchiveError('Pointer value is malformed')


def check_index(raw, pointer):
    """Fail closed unless the fetched bytes are exactly the index the pointer pins."""
    check_pointer(pointer)
    if ai.sha256(raw) != pointer['index_sha256']:
        raise ArchiveError('Index hash differs from the pointer')
    try:
        index = ai.loads(raw.decode('utf-8'))
    except UnicodeDecodeError as error:
        raise ArchiveError('Index is not UTF-8') from error
    if not isinstance(index, dict) or ai.index_bytes(index) != raw:
        raise ArchiveError('Index is not the canonical serialization')
    if index.get('format') != FORMAT or index.get('source_url') != ai.SOURCE_URL:
        raise ArchiveError('Index format or source differs')
    if type(index.get('version')) is not int or int(PATH.fullmatch(pointer['index_path']).group(1)) != index['version']:
        raise ArchiveError('Index version differs from its path')
    previous = index.get('previous')
    if index['version'] == 1:
        if previous is not None:
            raise ArchiveError('Version 1 names a previous index')
    elif not isinstance(previous, dict) or set(previous) != set(PREVIOUS_KEYS):
        raise ArchiveError('Later versions must name the previous index')
    if make_index(index.get('entries'), index['version'], previous) != index:
        raise ArchiveError('Index counts or entry hash differ')
    if index['entry_count'] != pointer['entries'] or make_pointer(raw, index, pointer['index_path'], pointer['index_commit']) != pointer:
        raise ArchiveError('Pointer count or key hash differs from the index')
    return index


def expand(actions, fetch):
    """Return the full object and, when present, the pointer and its index."""
    if not isinstance(actions, dict):
        raise ArchiveError(KEY + ' is not an object')
    if MARK not in actions:
        if any(is_stub(v) for v in actions.values()):
            raise ArchiveError('A stub without a pointer')
        return actions, None, None
    if next(iter(actions)) != MARK:
        raise ArchiveError('The pointer must be the first key')
    pointer = actions[MARK]
    check_pointer(pointer)
    if fetch is None:
        raise ArchiveError('The object starts with a pointer and no source for the index was given')
    index = check_index(fetch(pointer['index_commit'], pointer['index_path']), pointer)
    held = {item['key']: item['entry'] for item in index['entries']}
    stubs = {k for k, v in actions.items() if k != MARK and is_stub(v)}
    if stubs != set(held):
        raise ArchiveError('The stubs differ from the indexed keys')
    full = {}
    for key, value in actions.items():
        if key == MARK:
            continue
        if key in held:
            if value != stub_for(held[key]):
                raise ArchiveError('A stub differs from the indexed entry it stands for: ' + key)
            full[key] = held[key]
        else:
            full[key] = value
    return full, pointer, index


def resolve(body, fetch):
    """Rebuild the object as it was before any entries were archived."""
    prefix, state, suffix = ai.split_body(body)
    if KEY not in state:
        raise ArchiveError(KEY + ' is missing')
    state[KEY], pointer, _ = expand(state[KEY], fetch)
    return ai.join_body(prefix, state, suffix) if pointer else body


def migrate(body, raw, path, commit, fetch=None):
    """Replace the chosen entries by stubs and one pointer; nothing is returned unless the
    result expands to exactly what the input expands to."""
    prefix, state, suffix = ai.split_body(body)
    index = ai.loads(raw.decode('utf-8'))
    pointer = make_pointer(raw, index, path, commit)
    check_index(raw, pointer)
    full, old, old_index = expand(state[KEY], fetch)
    chosen = {item['key']: item['entry'] for item in index['entries']}
    for key, value in chosen.items():
        if key not in full or ai.compact(full[key]) != ai.compact(value):
            raise ArchiveError('The live entry differs from the indexed one; rebuild and re-review, never overwrite: ' + key)
    if old is None:
        if index['version'] != 1:
            raise ArchiveError('The first index must be version 1')
    else:
        held = {item['key']: item['entry'] for item in old_index['entries']}
        if index['version'] != old_index['version'] + 1 or not set(held) <= set(chosen):
            raise ArchiveError('A later version must follow the live one and keep every entry')
        if index['previous'] != {k: old[k] for k in PREVIOUS_KEYS}:
            raise ArchiveError('The index does not name the live index as previous')
    state[KEY] = {MARK: pointer}
    state[KEY].update({k: stub_for(v) if k in chosen else v for k, v in full.items()})
    after = ai.join_body(prefix, state, suffix)
    served = lambda c, p: raw if p == path else fetch(c, p)
    if resolve(after, served) != resolve(body, served):
        raise ArchiveError('Round trip differs from the original body')
    return after


def report(before, after, expanded):
    return {'before_chars': len(before), 'after_chars': len(after), 'saved_chars': len(before) - len(after),
            'headroom_after': ai.LIMIT - len(after), 'before_sha256': ai.sha256(before), 'after_sha256': ai.sha256(after),
            'expanded_sha256': ai.sha256(expanded)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('build', 'migrate', 'resolve', 'check'):
        step = sub.add_parser(name)
        step.add_argument('--body-file', required=True)
        step.add_argument('--comment-json', action='store_true', help='body-file is the GitHub API comment JSON')
        step.add_argument('--repo', default='.')
    sub.choices['build'].add_argument('--keys', required=True, help='comma separated keys, in live order')
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
    text = Path(args.body_file).read_text(encoding='utf-8')
    body, fetch = (ai.loads(text)['body'] if args.comment_json else text), ai.git_fetch(args.repo)
    try:
        if args.command == 'build':
            _, state, _ = ai.split_body(body)
            full, _, _ = expand(state[KEY], fetch)
            wanted = args.keys.split(',')
            missing = [k for k in wanted if k not in full]
            if missing or [k for k in full if k in wanted] != wanted:
                raise ArchiveError('Keys must exist and be named in live order: ' + ','.join(missing))
            previous = ai.loads(args.previous_json) if args.previous_json else None
            index = make_index([{'key': k, 'entry': full[k]} for k in wanted], args.version, previous)
            Path(args.out).write_bytes(ai.index_bytes(index))
            print(json.dumps({'index_sha256': ai.sha256(Path(args.out).read_bytes()), 'entries': len(wanted)}))
        elif args.command == 'migrate':
            raw = Path(args.index_file).read_bytes()
            after = migrate(body, raw, args.index_path, args.commit, fetch)
            expanded = resolve(after, lambda commit, path: raw if path == args.index_path else fetch(commit, path))
            Path(args.out).write_text(after, encoding='utf-8')
            print(json.dumps(report(body, after, expanded)))
        elif args.command == 'resolve':
            Path(args.out).write_text(resolve(body, fetch), encoding='utf-8')
            print(json.dumps({'sha256': ai.sha256(Path(args.out).read_bytes())}))
        else:
            _, state, _ = ai.split_body(body)
            full, pointer, index = expand(state[KEY], fetch)
            if pointer and args.ancestor_of and ai.subprocess.run(
                    ['git', '-C', args.repo, 'merge-base', '--is-ancestor', pointer['index_commit'], args.ancestor_of]).returncode:
                raise ArchiveError('Pinned commit is not reachable from ' + args.ancestor_of)
            print(json.dumps({'pointer': bool(pointer), 'entries': len(full), 'archived': index['entry_count'] if index else 0,
                              'inline': len(full) - (index['entry_count'] if index else 0)}))
    except ArchiveError as error:
        print('REFUSED: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
