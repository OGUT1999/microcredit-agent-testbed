"""Shared bounded JSON input for offline supplied-evidence CLIs.

Errors here are intentionally static; callers must not print exception text.
This is not filesystem authorization or a comprehensive resource sandbox.
"""
import argparse
import json
import stat
from pathlib import Path

MAX_RECORD_BYTES = 1024 * 1024


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON member")
        result[key] = value
    return result


def _finite_json(value):
    raise ValueError("nonstandard JSON number")


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError("invalid command arguments")


def read_record(argv, *, prog, description, argument_name="record"):
    parser = _Parser(prog=prog, description=description)
    parser.add_argument(argument_name, type=Path)
    args = parser.parse_args(argv)
    path = getattr(args, argument_name)
    if not stat.S_ISREG(path.stat().st_mode):
        raise ValueError("record must be a regular file")
    with path.open("rb") as handle:
        raw = handle.read(MAX_RECORD_BYTES + 1)
    if len(raw) > MAX_RECORD_BYTES:
        raise ValueError("record exceeds bounded input size")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object,
                      parse_constant=_finite_json)
