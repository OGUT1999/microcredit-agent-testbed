#!/usr/bin/env python3
"""Preparation checks only; no installation, model calls, RPC or signing.

Exit 0: selected offline checks passed. Exit 1: check failed. Exit 2: missing
runtime dependency prevents executor validation. None means rehearsal readiness.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    # Do not pass existing wallet, provider or GitHub credentials to children.
    env = {k: v for k, v in os.environ.items()
           if k in ("PATH", "SYSTEMROOT", "LANG", "LC_ALL", "TMPDIR")}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    results = []

    def run(label, command):
        try:
            result = subprocess.run(command, cwd=ROOT, env=env, text=True,
                                    capture_output=True, timeout=120)
            row = {"check": label, "status": "passed" if result.returncode == 0 else "failed",
                   "exitCode": result.returncode,
                   "output": (result.stdout + result.stderr).strip()}
        except (OSError, subprocess.TimeoutExpired) as error:
            row = {"check": label, "status": "failed", "output": type(error).__name__}
        results.append(row)
        return row

    run("market and receipt bridge", [sys.executable, "-m", "unittest", "discover",
                                     "-s", str(HERE), "-p", "test_*.py"])
    for file in sorted(HERE.glob("*.mjs")):
        run("syntax: " + file.name, ["node", "--check", str(file)])
    for file in ("comment-launcher.mjs", "fixture-builder.mjs"):
        run(file + " self-test", ["node", str(HERE / file), "--self-test"])
    # --validate exits before wallet construction. Deliberately do not run
    # executor --self-test: that test creates a random wallet and signs data.
    runtime = HERE / "runtime"
    if (runtime / "node_modules/ethers/package.json").is_file():
        # Node resolves dependencies from the module's directory. Copy exact
        # executor bytes into a disposable child of the isolated runtime;
        # leave the live entrypoint and all other project dependencies alone.
        with tempfile.TemporaryDirectory(prefix="metadata-check-", dir=runtime) as directory:
            executor = Path(directory) / "executor.mjs"
            executor.write_bytes((HERE / "executor.mjs").read_bytes())
            validation = run("executor metadata validation", ["node", str(executor), "--validate"])
    else:
        validation = run("executor metadata validation", ["node", str(HERE / "executor.mjs"), "--validate"])
    if "ERR_MODULE_NOT_FOUND" in validation["output"] and "Cannot find package 'ethers'" in validation["output"]:
        validation.update(status="blocked", output="Existing ethers@6.15.0 dependency missing; nothing installed.")
    for name in ("guarantee-trust-real-agents.yml", "guarantee-trust-real-agents-comment.yml"):
        text = (ROOT / ".github/workflows" / name).read_text()
        guards = [line.strip() for line in text.splitlines() if line.startswith("    if:")]
        results.append({"check": name + " disabled job guard",
                        "status": "passed" if guards == ["if: ${{ false }}"] else "failed"})
    artifact = ROOT / "experiments/guarantee-trust-circle-coldstart/artifact.json"
    artifact_hash = hashlib.sha256(artifact.read_bytes()).hexdigest()
    results.append({"check": "pinned artifact SHA256", "status": "passed" if artifact_hash ==
                    "9589450dbe08cbf1907fd68e8dc82c341346163b7d19da9a4052f248e60c5612" else "failed"})
    failed = any(row["status"] == "failed" for row in results)
    blocked = any(row["status"] == "blocked" for row in results)
    print(json.dumps({"schema": "real-agents-offline-preparation/1", "checks": results,
                      "sourceSha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                       for p in sorted(HERE.iterdir()) if p.suffix in (".mjs", ".py")},
                      "runtimeSha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                        for p in sorted(runtime.glob("*.json"))},
                      "modelInvocations": 0, "EVMExecuted": False, "signingExecuted": False,
                      "readyForLiveExecution": False}, indent=2))
    return 1 if failed else 2 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
