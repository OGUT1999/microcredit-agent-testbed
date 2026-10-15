"""Real local Git fixtures; no GitHub write, network, hook or live operation."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

try:
    from . import ordinary_evidence_preflight as preflight
except ImportError:
    import ordinary_evidence_preflight as preflight


EMAIL = "fixture@users.noreply.github.com"
PATHS = [f"evidence/source-r1/{name}" for name in sorted(preflight.RECORDS)]


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.env = {**os.environ, "GIT_AUTHOR_NAME": "Fixture AI", "GIT_COMMITTER_NAME": "Fixture AI",
                    "GIT_AUTHOR_EMAIL": EMAIL, "GIT_COMMITTER_EMAIL": EMAIL}
        self.git("init", "-q")
        self.git("config", "commit.gpgsign", "false")
        self.write("anchor.txt", "base\n")
        self.base = self.commit()
        for path in PATHS:
            self.write(path, "synthetic fixture\n")
        self.head = self.commit()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, env=self.env, check=True,
                              capture_output=True, text=True).stdout.strip()

    def write(self, path, text):
        dest = self.repo / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")

    def commit(self):
        self.git("add", "--all")
        self.git("commit", "-qm", "Synthetic fixture")
        return self.git("rev-parse", "HEAD")

    def inspect(self, **kwargs):
        args = dict(repo=self.repo, base=self.base, head=self.head, expected_paths=PATHS,
                    author_email=EMAIL, committer_email=EMAIL)
        args.update(kwargs)
        return preflight.inspect(**args)

    def rejected(self, reason, **kwargs):
        with self.assertRaisesRegex(preflight.Rejected, "^" + reason + "$"):
            self.inspect(**kwargs)

    def test_exact_packet_and_no_authorization(self):
        before = self.git("show-ref")
        result = self.inspect()
        self.assertEqual(result["status"], "LOCAL_METADATA_MATCH_ONLY")
        self.assertFalse(result["authorization"])
        self.assertFalse(result["writes_performed"])
        self.assertEqual(result["path_count"], 3)
        self.assertEqual(before, self.git("show-ref"))

    def test_packet_plus_roadmap(self):
        self.write(preflight.ROADMAP, "fixture\n")
        self.git("add", "--all")
        self.git("commit", "--amend", "--no-edit", "-q")
        result = self.inspect(head=self.git("rev-parse", "HEAD"), expected_paths=PATHS + [preflight.ROADMAP])
        self.assertEqual(result["path_count"], 4)

    def test_stale_base_after_concurrent_commit(self):
        self.write("concurrent.txt", "preserve\n")
        newer = self.commit()
        self.rejected("SOLE_PARENT_MUST_EQUAL_BASE", base=newer)

    def test_multiple_commits_not_one_reviewed_increment(self):
        self.write(PATHS[0], "changed again\n")
        self.rejected("SOLE_PARENT_MUST_EQUAL_BASE", head=self.commit())

    def test_unexpected_protected_change(self):
        self.write("world-model/model.json", "{}\n")
        self.git("add", "--all")
        self.git("commit", "--amend", "--no-edit", "-q")
        self.rejected("EXACT_PATH_SET_MISMATCH", head=self.git("rev-parse", "HEAD"))

    def test_protected_path_cannot_be_declared(self):
        self.rejected("ORDINARY_PACKET_SCOPE_REQUIRED", expected_paths=PATHS + ["world-model/model.json"])

    def test_duplicates_and_incomplete_packets(self):
        for paths in (PATHS + [PATHS[0]], PATHS[:2], [], PATHS + [1]):
            with self.subTest(paths=paths):
                self.rejected("ORDINARY_PACKET_SCOPE_REQUIRED", expected_paths=paths)

    def test_noncanonical_scope(self):
        for name in ("../source-r1", "two/levels", "SOURCE", "source_r1", "private\nvalue"):
            self.rejected("ORDINARY_PACKET_SCOPE_REQUIRED", expected_paths=[f"evidence/{name}/{p}" for p in preflight.RECORDS])

    def test_two_packet_scope(self):
        self.rejected("ORDINARY_PACKET_SCOPE_REQUIRED", expected_paths=[PATHS[0].replace("source-r1", "other")] + PATHS[1:])

    def test_revision_expression_and_option_rejected(self):
        for value in ("HEAD", "HEAD~1", "--help", self.head.upper(), "f" * 39):
            self.rejected("EXACT_COMMIT_IDS_REQUIRED", head=value)

    def test_tree_is_not_commit(self):
        self.rejected("EXACT_COMMIT_IDS_REQUIRED", head=self.git("rev-parse", "HEAD^{tree}"))

    def test_missing_object_static_failure(self):
        self.rejected("LOCAL_GIT_READ_FAILED", head="0" * 40)

    def test_both_exact_identities_required(self):
        self.rejected("COMMIT_IDENTITY_MISMATCH", committer_email="other@users.noreply.github.com")
        self.rejected("COMMIT_IDENTITY_MISMATCH", author_email="other@users.noreply.github.com")

    def test_personal_or_lookalike_expectation_rejected(self):
        for email in ("private@example.org", "fixture@users.noreply.github.com.evil", "X\n@users.noreply.github.com"):
            self.rejected("NOREPLY_EXPECTATION_REQUIRED", author_email=email)

    def test_actual_personal_committer_rejected(self):
        self.env["GIT_COMMITTER_EMAIL"] = "private@example.org"
        self.git("commit", "--amend", "--no-edit", "-q")
        self.rejected("COMMIT_IDENTITY_MISMATCH", head=self.git("rev-parse", "HEAD"))

    def test_empty_commit_rejected(self):
        self.git("checkout", "-q", "--detach", self.base)
        self.git("commit", "--allow-empty", "-qm", "Synthetic empty control")
        self.rejected("EXACT_DIFF_REQUIRED", head=self.git("rev-parse", "HEAD"))

    def test_symlink_rejected(self):
        (self.repo / PATHS[0]).unlink()
        (self.repo / PATHS[0]).symlink_to("../../anchor.txt")
        self.git("add", "--all")
        self.git("commit", "--amend", "--no-edit", "-q")
        self.rejected("REGULAR_ADDITIONS_OR_MODIFICATIONS_ONLY", head=self.git("rev-parse", "HEAD"))

    def test_executable_rejected(self):
        self.git("update-index", "--chmod=+x", PATHS[0])
        self.git("commit", "--amend", "--no-edit", "-q")
        self.rejected("REGULAR_ADDITIONS_OR_MODIFICATIONS_ONLY", head=self.git("rev-parse", "HEAD"))

    def test_deletion_rejected(self):
        (self.repo / "anchor.txt").unlink()
        self.git("add", "--all")
        self.git("commit", "--amend", "--no-edit", "-q")
        self.rejected("REGULAR_ADDITIONS_OR_MODIFICATIONS_ONLY", head=self.git("rev-parse", "HEAD"))

    def test_replacement_and_graft_rejected(self):
        self.git("replace", self.head, self.base)
        self.rejected("UNALTERED_HISTORY_REQUIRED")
        self.git("replace", "-d", self.head)
        self.write(".git/info/grafts", "")
        self.rejected("UNALTERED_HISTORY_REQUIRED")

    def test_partial_and_shallow_rejected(self):
        self.git("config", "remote.origin.promisor", "true")
        self.rejected("COMPLETE_LOCAL_REPOSITORY_REQUIRED")
        self.git("config", "--unset", "remote.origin.promisor")
        self.write(".git/shallow", self.head + "\n")
        self.rejected("COMPLETE_LOCAL_REPOSITORY_REQUIRED")

    def test_worktree_promisor_configuration_rejected(self):
        self.git("config", "extensions.worktreeConfig", "true")
        self.git("config", "--worktree", "remote.origin.promisor", "true")
        self.rejected("COMPLETE_LOCAL_REPOSITORY_REQUIRED")

    def test_included_partial_clone_configuration_rejected(self):
        self.write(".git/included-config", "[extensions]\n\tpartialClone = origin\n")
        self.git("config", "include.path", "included-config")
        self.rejected("COMPLETE_LOCAL_REPOSITORY_REQUIRED")

    def test_cli_failures_do_not_echo_inputs(self):
        for args in (["--private-option-secret"], ["--repo", "/private/path", "--base", "secret"]):
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = preflight.main(args)
            self.assertEqual(code, 1)
            self.assertEqual(json.loads(out.getvalue())["reason"], "INVALID_ARGUMENTS")
            self.assertEqual(err.getvalue(), "")
            self.assertNotIn("secret", out.getvalue())
            self.assertNotIn("private", out.getvalue())

    def test_git_environment_no_lazy_fetch_or_overrides(self):
        with patch.dict(os.environ, {"GIT_TRACE": "/private/trace", "GIT_DIR": "/private/repo"}):
            with patch.object(preflight.subprocess, "run") as run:
                preflight.git(self.repo, "cat-file", "-t", self.head)
                env = run.call_args.kwargs["env"]
                self.assertEqual(env["GIT_NO_LAZY_FETCH"], "1")
                self.assertNotIn("GIT_TRACE", env)
                self.assertNotIn("GIT_DIR", env)


if __name__ == "__main__":
    unittest.main()
