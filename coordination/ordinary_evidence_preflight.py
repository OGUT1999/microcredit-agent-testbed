#!/usr/bin/env python3
"""Offline metadata prerequisite for an existing ordinary-evidence commit.

No network, ref update, commit creation, merge, content review or authorization.
The protected Git-shell lease protocol is deliberately outside this tool.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess


ROADMAP = "coordination/POVERTY_ELIMINATION_ROADMAP.md"
RECORDS = {"README.md", "sources.json", "validation.json"}
OID = re.compile(r"[0-9a-f]{40}")
PACKET = re.compile(r"evidence/([a-z0-9][a-z0-9-]{0,95})/(README\.md|sources\.json|validation\.json)")
NOREPLY = re.compile(r"[A-Za-z0-9][A-Za-z0-9+._-]{0,100}@users\.noreply\.github\.com")
REMAINING = ["fresh remote base and source readback", "current authority and branch policy",
             "non-author content and archive-integrity review", "required CI and public-content checks",
             "non-forcing server fast-forward", "independent default-branch receipt"]


class Rejected(Exception):
    """Static reason only; never carry input, Git stderr, paths or identities."""


def reject(reason):
    raise Rejected(reason)


def git(repo, *args):
    # Discard inherited Git overrides/tracing. Object reads must not lazy-fetch.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1", GIT_OPTIONAL_LOCKS="0",
               GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, LC_ALL="C")
    return subprocess.run(["git", "-c", "core.fsmonitor=false", *args], cwd=repo,
                          env=env, capture_output=True, check=True, timeout=10).stdout


def identity_safe(email):
    return isinstance(email, str) and (NOREPLY.fullmatch(email) is not None or email == "noreply@anthropic.com")


def inspect(repo, base, head, expected_paths, author_email, committer_email):
    """Return local metadata evidence, or static rejection. No write is performed."""
    if not isinstance(base, str) or not OID.fullmatch(base) or not isinstance(head, str) or not OID.fullmatch(head):
        reject("EXACT_COMMIT_IDS_REQUIRED")
    if not identity_safe(author_email) or not identity_safe(committer_email):
        reject("NOREPLY_EXPECTATION_REQUIRED")
    if not isinstance(expected_paths, (list, tuple)) or len(expected_paths) not in (3, 4):
        reject("ORDINARY_PACKET_SCOPE_REQUIRED")
    if any(not isinstance(p, str) for p in expected_paths) or len(set(expected_paths)) != len(expected_paths):
        reject("ORDINARY_PACKET_SCOPE_REQUIRED")
    records = [p for p in expected_paths if p != ROADMAP]
    matches = [PACKET.fullmatch(p) for p in records]
    if (len(records) != 3 or not all(matches) or len({m[1] for m in matches}) != 1
            or {m[2] for m in matches} != RECORDS):
        reject("ORDINARY_PACKET_SCOPE_REQUIRED")
    try:
        # A complete local object store is a precondition, not a download request.
        if git(repo, "rev-parse", "--is-shallow-repository").strip() != b"false":
            reject("COMPLETE_LOCAL_REPOSITORY_REQUIRED")
        config = git(repo, "config", "--includes", "--list").lower()
        if b"partialclone" in config or b".promisor=" in config or b".partialclonefilter=" in config:
            reject("COMPLETE_LOCAL_REPOSITORY_REQUIRED")
        if git(repo, "for-each-ref", "--format=%(refname)", "refs/replace/").strip():
            reject("UNALTERED_HISTORY_REQUIRED")
        grafts = git(repo, "rev-parse", "--git-path", "info/grafts").decode().strip()
        graft_path = Path(grafts)
        if not graft_path.is_absolute():
            graft_path = Path(repo) / graft_path
        if graft_path.exists():
            reject("UNALTERED_HISTORY_REQUIRED")
        if git(repo, "cat-file", "-t", base).strip() != b"commit" or git(repo, "cat-file", "-t", head).strip() != b"commit":
            reject("EXACT_COMMIT_IDS_REQUIRED")
        # Raw headers, not log's possibly rewritten topology; ignore message text.
        headers = git(repo, "cat-file", "commit", head).split(b"\n\n", 1)[0].splitlines()
        parents = [v[7:].decode("ascii") for v in headers if v.startswith(b"parent ")]
        if parents != [base]:
            reject("SOLE_PARENT_MUST_EQUAL_BASE")
        for label, expected in ((b"author ", author_email), (b"committer ", committer_email)):
            fields = [v for v in headers if v.startswith(label)]
            match = re.fullmatch(rb"[^\n]* <([^<>\n]+)> [0-9]+ [+-][0-9]{4}", fields[0]) if len(fields) == 1 else None
            if not match or match[1].decode("ascii") != expected:
                reject("COMMIT_IDENTITY_MISMATCH")
        raw = git(repo, "diff-tree", "-r", "--raw", "--no-abbrev", "--no-renames",
                  "--no-ext-diff", "--no-textconv", "-z", base, head, "--")
        parts = raw.split(b"\0")
        if not raw or parts[-1] != b"" or len(parts[:-1]) % 2:
            reject("EXACT_DIFF_REQUIRED")
        actual = []
        for metadata, name in zip(parts[0:-1:2], parts[1:-1:2]):
            fields = metadata.split()
            if (len(fields) != 5 or fields[4] not in (b"A", b"M") or fields[1] != b"100644"
                    or fields[0] != (b":000000" if fields[4] == b"A" else b":100644")):
                reject("REGULAR_ADDITIONS_OR_MODIFICATIONS_ONLY")
            actual.append(name.decode("ascii"))
        if len(actual) != len(expected_paths) or set(actual) != set(expected_paths):
            reject("EXACT_PATH_SET_MISMATCH")
        tree = [v[5:].decode("ascii") for v in headers if v.startswith(b"tree ")]
        if len(tree) != 1 or not OID.fullmatch(tree[0]):
            reject("EXACT_DIFF_REQUIRED")
        return {"status": "LOCAL_METADATA_MATCH_ONLY", "authorization": False,
                "base": base, "head": head, "tree": tree[0], "path_count": len(actual),
                "writes_performed": False, "remaining_gates": REMAINING}
    except Rejected:
        raise
    except (OSError, ValueError, UnicodeError, subprocess.SubprocessError):
        reject("LOCAL_GIT_READ_FAILED")


class Parser(argparse.ArgumentParser):
    def error(self, message):
        reject("INVALID_ARGUMENTS")


def main(argv=None):
    try:
        parser = Parser(description=__doc__)
        parser.add_argument("--repo", default=".")
        parser.add_argument("--base", required=True)
        parser.add_argument("--head", required=True)
        parser.add_argument("--path", action="append", required=True)
        parser.add_argument("--author-email", required=True)
        parser.add_argument("--committer-email", required=True)
        args = parser.parse_args(argv)
        result = inspect(args.repo, args.base, args.head, args.path, args.author_email, args.committer_email)
        code = 0
    except Rejected as error:
        result = {"status": "REJECTED", "reason": str(error), "authorization": False, "writes_performed": False}
        code = 1
    print(json.dumps(result, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
