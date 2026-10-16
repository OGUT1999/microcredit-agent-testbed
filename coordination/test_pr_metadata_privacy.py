"""Execute the actual read-only CI metadata step; no network or real secrets.

CI detects metadata after publication, including edits. It does not prevent the
initial exposure, inspect comments/history, or replace prepublication checks.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/world-model.yml"


def metadata_step():
    source = WORKFLOW.read_text(encoding="utf-8")
    section = source.split("      - name: PR metadata privacy check\n", 1)[1]
    section = section.split("      - run:", 1)[0]
    return textwrap.dedent(section.split("        run: |\n", 1)[1])


class PRMetadataPrivacyTests(unittest.TestCase):
    def run_step(self, payload, *, raw=False, stale=False):
        with tempfile.TemporaryDirectory(prefix="pr-metadata-test-") as directory:
            temporary = Path(directory)
            event = temporary / "event.json"
            event.write_text(payload if raw else json.dumps(payload), encoding="utf-8")
            if stale:
                (temporary / "pr-metadata.stale").write_text("safe old input", encoding="utf-8")
            environment = dict(os.environ, GITHUB_EVENT_PATH=str(event), RUNNER_TEMP=directory)
            result = subprocess.run(["bash", "-c", metadata_step()], cwd=ROOT,
                                    env=environment, capture_output=True, text=True, timeout=10)
            remaining = sorted(path.name for path in temporary.iterdir())
            self.assertEqual(remaining, ["event.json", "pr-metadata.stale"] if stale else ["event.json"])
            self.assertFalse((ROOT / "metadata-command-executed").exists())
            return result

    def test_clean_multilingual_and_null_body(self):
        for body in ("Useful review — trabajo, 收入", "", None):
            with self.subTest(body=body):
                result = self.run_step({"pull_request": {"title": "Safe change", "body": body}})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout + result.stderr, "")

    def test_forbidden_identifiers_in_each_field_are_not_logged(self):
        # Assemble synthetic fixtures so repository content itself stays public-safe.
        examples = ["https://claude.ai/code/" + "session_" + "01" + "A" * 24,
                    "ghp" + "_" + "B" * 24]
        for field in ("title", "body"):
            for example in examples:
                with self.subTest(field=field, kind=examples.index(example)):
                    fields = {"title": "Safe title", "body": "Safe description"}
                    fields[field] = "private surrounding text " + example
                    result = self.run_step({"pull_request": fields})
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(result.stdout, "")
                    self.assertEqual(result.stderr, "PR metadata privacy check failed; inspect title and description privately.\n")
                    self.assertNotIn(example, result.stdout + result.stderr)
                    self.assertNotIn("private surrounding text", result.stdout + result.stderr)

    def test_shell_syntax_is_inert_data(self):
        value = '$(touch metadata-command-executed) `touch metadata-command-executed` " ; exit 99 #\nPY\n'
        result = self.run_step({"pull_request": {"title": value, "body": value}})
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_malformed_and_missing_inputs_fail_closed_without_echo(self):
        payloads = ["{secret invalid input", "[]", "{}", '{"pull_request": null}',
                    '{"pull_request": {"title": "safe"}}',
                    '{"pull_request": {"body": "safe"}}']
        for payload in payloads:
            with self.subTest(payload=payload):
                result = self.run_step(payload, raw=True, stale=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertEqual(result.stderr, "PR metadata unavailable or invalid; privacy check failed.\n")

    def test_wrong_types_and_nul_fail_closed(self):
        for title, body in ((None, "safe"), ([], "safe"), ("safe", {}),
                            ("safe", False), (1, "safe"), ("safe", "a\0b")):
            with self.subTest(title=title, body=body):
                result = self.run_step({"pull_request": {"title": title, "body": body}})
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stderr, "PR metadata unavailable or invalid; privacy check failed.\n")

    def test_workflow_scope_and_existing_guard_are_preserved(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("types: [opened, synchronize, reopened, edited]", source)
        self.assertIn("if: github.event_name == 'pull_request'", source)
        self.assertIn("contents: read", source)
        self.assertIn("persist-credentials: false", source)
        self.assertIn('bash world-model/check-public-content.sh --range "$base..HEAD"', source)
        self.assertNotIn("pull_request_target", source)
        self.assertNotIn("${{", metadata_step())
        self.assertNotIn("GITHUB_OUTPUT", metadata_step())
        self.assertNotIn("GITHUB_ENV", metadata_step())


if __name__ == "__main__":
    unittest.main()
