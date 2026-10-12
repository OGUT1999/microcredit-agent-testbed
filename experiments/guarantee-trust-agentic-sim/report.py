"""Summarises a run: per-day activity from events.jsonl, the chain snapshot, messages and journals.
usage: python3 report.py RUN_DIR [--day D] [--messages] [--journals] [--agent NAME]"""
import argparse
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))


def load_events(run):
    return [json.loads(l) for l in open(os.path.join(run, "events.jsonl"))]


def env_call(run, cmd):
    keys = json.load(open(os.path.join(run, "secrets", "keys.json")))
    r = subprocess.run([sys.executable, os.path.join(HERE, "sim.py"), "--me", "__env__", "--token", keys["__env__"]["token"], cmd],
                       capture_output=True, text=True)
    return {"result": json.loads(r.stdout)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--day", type=int)
    ap.add_argument("--messages", action="store_true")
    ap.add_argument("--journals", action="store_true")
    ap.add_argument("--agent")
    ap.add_argument("--snapshot", action="store_true")
    a = ap.parse_args()
    ev = load_events(a.run)
    if a.day:
        ev = [e for e in ev if e["day"] == a.day]
    if a.agent:
        ev = [e for e in ev if e["agent"] == a.agent]
        for e in ev:
            print(f"d{e['day']} {e['cmd']} {json.dumps(e['args'])[:160]} -> {'ok' if e['ok'] else 'REFUSED'}: {str(e['result'])[:200]}")
        return
    cmds = Counter(e["cmd"] for e in ev if e["agent"] != "__env__")
    refused = Counter((e["cmd"], str(e["result"])[:90]) for e in ev if not e["ok"] and e["agent"] != "__env__")
    agents = Counter(e["agent"] for e in ev if e["agent"] != "__env__")
    print("commands:", dict(cmds.most_common()))
    print("active agents:", len(agents), "; commands per agent: min", min(agents.values(), default=0), "max", max(agents.values(), default=0))
    print("refusals:")
    for (c, r), n in refused.most_common(40):
        print(f"  {n:3d} {c}: {r}")
    state = json.load(open(os.path.join(a.run, "state.json")))
    jobs = state["jobs"].values()
    print("jobs by status:", dict(Counter(j["status"] for j in jobs)))
    if a.snapshot:
        s = env_call(a.run, "snapshot")["result"]
        g = s["guarantees"]
        print("day", s["day"], "reserve", s["reserve"] / 1e6, "outstanding", s["outstanding"] / 1e6, "stake", s["totalStake"] / 1e6,
              "dues", s["totalDues"] / 1e6, "sponsorCapital", s["sponsorCapital"] / 1e6, "issuer held/spent",
              s["issuerHeld"] / 1e6, s["issuerSpent"] / 1e6, "supply", s["supply"] / 1e6)
        print("identities:", s["identity_token_eq_reserve_plus_stake"], s["identity_reserve_eq_sponsor_plus_dues"])
        print("guarantees (this experiment):", len(g), dict(Counter(x["state"] for x in g)))
        for x in g:
            print(f"  #{x['id']} {x['state']:9s} worker={x['worker']:20s} client={x['client']:20s} G={x['amount']} backing={x['fromBacking']} line={x['fromLine']} dues={x['fromDues']} wage={x['wage_recorded']} due={x['contributionDue']} remitted={x['remitted']} lapsed={x['lapsed']} job={x['job']}")
    if a.messages:
        for m in state["messages"]:
            if not a.day or m["day"] == a.day:
                print(f"d{m['day']} {m['from']} -> {m['to']}: {m['text']}")
    if a.journals:
        for n, js in state["journals"].items():
            for d, t in js.items():
                if not a.day or int(d) == a.day:
                    print(f"[{n} d{d}] {t}\n")


if __name__ == "__main__":
    main()
