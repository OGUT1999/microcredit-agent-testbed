"""One explicitly instrumented setup observation, not a recurring benchmark.

Run only for the authorized one-shot or after an attributable reopening receipt.
The observer reports Python-level observations, not full OS/native closure.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import time

PIN = "f3ce81ba1a772faef83d4c2f14ec752e96f53bf0"
COMMAND = ["-m", "unittest", "discover", "-s", "metrics", "-p",
           "test_human_outcome_cash.py", "-v"]
FIXTURE = "evidence/human-outcome-cli-privacy-20261014/precision-limitation.json"
MARKER = "BOT_SETUP_OBSERVER="
OBSERVER = r'''import sys
_startup = dict(sys.modules)
import atexit
_observer_bootstrap = set(sys.modules) - set(_startup)
_attempted = set()
_opens = []
def _audit(event, args):
    if event == "import" and args and isinstance(args[0], str):
        _attempted.add(args[0])
    if event == "open" and len(_opens) < 5000 and args:
        _opens.append((args[0], args[1] if len(args) > 1 else None))
sys.addaudithook(_audit)
def _finish():
    final = dict(sys.modules)
    attempts = sorted(_attempted)
    opens = list(_opens)
    import json, os, hashlib
    helpers = sorted(set(sys.modules) - set(final))
    repo = os.environ["BOT_SETUP_REPO"]
    observer = os.environ["BOT_SETUP_OBSERVER"]
    stdlib = os.path.join(sys.base_prefix, "lib", "python%d.%d" % sys.version_info[:2])
    def origin(path):
        if path in (None, "built-in", "frozen"):
            return path
        if not isinstance(path, str):
            return "UNATTRIBUTED"
        absolute = os.path.abspath(path)
        for root, label in ((repo,"<repo>"),(observer,"<observer>"),(stdlib,"<stdlib>"),(sys.prefix,"<venv>")):
            if absolute == root or absolute.startswith(root + os.sep):
                rel = os.path.relpath(absolute, root)
                if label == "<stdlib>" and "site-packages" in rel.split(os.sep):
                    return "UNATTRIBUTED_SITE_PACKAGE"
                return label + "/" + rel
        if absolute.startswith(temp_root + os.sep):
            return "<temporary-test-input>"
        return "UNATTRIBUTED"
    temp_root = os.environ["TMPDIR"]
    modules = []
    for name, module in sorted(final.items()):
        spec = getattr(module, "__spec__", None)
        path = getattr(spec, "origin", None)
        if path is None:
            path = getattr(module, "__file__", None)
        normalized = origin(path)
        digest = None
        if isinstance(normalized, str) and normalized.startswith(("<repo>/", "<observer>/", "<stdlib>/")) and os.path.isfile(path):
            with open(path, "rb") as handle:
                digest = hashlib.sha256(handle.read()).hexdigest()
        locations = getattr(spec, "submodule_search_locations", None)
        modules.append({"name":name,"origin":normalized,"sha256":digest,
                        "namespace_locations":[origin(p) for p in locations] if path is None and locations else [],
                        "phase":"observer_bootstrap" if name in _observer_bootstrap or name == "sitecustomize" else "startup" if name in _startup else "command_or_later"})
    payload = {"runtime":sys.version.split()[0],"platform":sys.platform,
               "venv_prefix_differs":sys.prefix != sys.base_prefix,
               "modules":modules,"attempted_import_names":attempts,
               "observer_serialization_added":helpers,
               "open_events":[{"origin":origin(p),"mode":m} for p,m in opens],
               "open_event_cap_reached":len(opens) >= 5000}
    sys.__stderr__.write("BOT_SETUP_OBSERVER=" + json.dumps(payload, sort_keys=True) + "\n")
atexit.register(_finish)
'''


def bounded(argv, *, cwd, env, seconds):
    process = subprocess.Popen(argv, cwd=cwd, env=env, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, start_new_session=True)
    try:
        out, err = process.communicate(timeout=seconds)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        raise ValueError("owned child timeout") from None
    return process.returncode, out, err


def observe(source):
    pin = subprocess.run(["git", "rev-parse", "HEAD"], cwd=source,
                         capture_output=True, text=True, check=True).stdout.strip()
    if pin != PIN or subprocess.run(["git", "diff", "--quiet", "HEAD"], cwd=source).returncode:
        raise ValueError("source pin differs")
    tree = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=source,
                          capture_output=True, text=True, check=True).stdout.strip()
    fixture = hashlib.sha256((source / FIXTURE).read_bytes()).hexdigest()
    env = {"PATH":os.defpath, "LANG":"C.UTF-8", "PYTHONDONTWRITEBYTECODE":"1",
           "PYTHONNOUSERSITE":"1"}
    started = datetime.now(timezone.utc).isoformat()
    with tempfile.TemporaryDirectory(prefix="bot-setup-once-") as temp:
        root = Path(temp)
        venv = root / "venv"
        beginning = time.perf_counter()
        rc, _, _ = bounded([sys.executable, "-m", "venv", "--without-pip", str(venv)],
                           cwd=source, env=env, seconds=15)
        setup_seconds = time.perf_counter() - beginning
        if rc:
            return {"status":"SETUP_FAILED", "setup_exit":rc,
                    "checked_at":started,"source_commit":PIN,"source_tree":tree}
        cfg = (venv / "pyvenv.cfg").read_text()
        observer = root / "observer"
        observer.mkdir()
        (observer / "sitecustomize.py").write_text(OBSERVER, encoding="utf-8")
        test_temp = root / "test-temp"
        test_temp.mkdir()
        env.update(PYTHONPATH=str(observer), BOT_SETUP_REPO=str(source),
                   BOT_SETUP_OBSERVER=str(observer), TMPDIR=str(test_temp))
        beginning = time.perf_counter()
        rc, out, err = bounded([str(venv / "bin/python"), *COMMAND],
                               cwd=source, env=env, seconds=15)
        execution_seconds = time.perf_counter() - beginning
        lines = err.splitlines()
        records = [line[len(MARKER):] for line in lines if line.startswith(MARKER)]
        tests = [line for line in lines if re.fullmatch(r"test_[a-z0-9_]+ \(.*\) \.\.\. ok", line)]
        observed = json.loads(records[0]) if len(records) == 1 else None
        exact = rc == 0 and len(tests) == 11 and "OK" in lines and any(re.fullmatch(r"Ran 11 tests in .*s", line) for line in lines)
        unattributed = [x["name"] for x in (observed or {}).get("modules", [])
                        if str(x["origin"]).startswith("UNATTRIBUTED")]
        isolated = "include-system-site-packages = false" in cfg and (observed or {}).get("venv_prefix_differs")
        repo_modules = [x for x in (observed or {}).get("modules", [])
                        if str(x["origin"]).startswith("<repo>/")]
        return {"schema":"botrepro002-setup-observation/1", "checked_at":started,
                "status":"INSTRUMENTED_SETUP_PASS" if exact and isolated and not unattributed else "SETUP_NOT_ESTABLISHED",
                "source_commit":PIN,"source_tree":tree,
                "command":["<venv>/bin/python", *COMMAND],
                "setup_command":["<base-python>","-m","venv","--without-pip","<venv>"],
                "setup_exit":0,"setup_seconds":setup_seconds,"execution_exit":rc,
                "execution_seconds_instrumented":execution_seconds,"setup_attempts":1,"test_executions":1,
                "package_installs":0,"downloads_performed_by_harness":0,
                "include_system_site_packages":False,"pip_bootstrap":False,
                "isolation_checks_passed":bool(isolated),
                "venv_site_packages_empty":not any((venv / "lib" / ("python%d.%d" % sys.version_info[:2]) / "site-packages").iterdir()),
                "observer_sha256":hashlib.sha256(OBSERVER.encode()).hexdigest(),
                "environment_interventions":["minimal inherited environment","PYTHONPATH=<observer>","PYTHONNOUSERSITE=1","PYTHONDONTWRITEBYTECODE=1","TMPDIR=<temporary-test-input>"],
                "tests":[line.split(" (")[0] for line in tests],"expected_groups":11,
                "stdout_sha256":hashlib.sha256(out.encode()).hexdigest(),
                "raw_stderr_sha256_private_not_published":hashlib.sha256(err.encode()).hexdigest(),
                "repository_module_inputs":repo_modules,
                "immutable_data_inputs":[{"path":FIXTURE,"sha256":fixture}],
                "generated_data_inputs":"Synthetic temporary JSON records generated from the pinned test code; no external participant records.",
                "unattributed_module_names":unattributed,"observation":observed,
                "additional_paid_software_dependency_established":False if exact and isolated and not unattributed else None,
                "full_os_native_or_other_platform_closure_established":False,
                "worker_effort_price_device_access_and_payout":None,
                "human_earnings_established":False,"financial_authority":False,
                "decision":"NO_OFFER_NO_LOAN_NO_GUARANTEE"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--record", type=Path, required=True)
    args = parser.parse_args()
    if args.record.exists():
        print('{"status":"EXISTING_RECORD_NOT_OVERWRITTEN"}')
        return 2
    try:
        record = observe(args.source.resolve())
        args.record.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"status":record["status"],"source_commit":PIN,
                          "tests":len(record.get("tests",[]))}))
    except Exception:
        print('{"status":"SETUP_CAPTURE_FAILED","human_earnings_established":false}')
        return 2
    return 0 if record["status"] == "INSTRUMENTED_SETUP_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
