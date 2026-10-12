#!/usr/bin/env python3
"""Agent-side CLI for the GuaranteeTrust agentic simulation. Talks to world.py; see `help`."""
import argparse
import json
import os
import sys
import urllib.request

URL = os.environ.get("SIM_URL", "http://127.0.0.1:8787")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--me", required=True)
    ap.add_argument("--token", required=True)
    ap.add_argument("cmd")
    ap.add_argument("pos", nargs="*")
    ap.add_argument("--text"); ap.add_argument("--title"); ap.add_argument("--description"); ap.add_argument("--wage")
    ap.add_argument("--days"); ap.add_argument("--ask"); ap.add_argument("--pitch"); ap.add_argument("--guarantee")
    ap.add_argument("--note"); ap.add_argument("--verdict"); ap.add_argument("--settle-days"); ap.add_argument("--max-dues")
    ap.add_argument("--which"); ap.add_argument("--role"); ap.add_argument("--deny", action="store_true"); ap.add_argument("--n")
    a = ap.parse_args()
    args = {k.replace("-", "_"): v for k, v in vars(a).items() if k not in ("me", "token", "cmd", "pos") and v not in (None, False)}
    p = a.pos
    c = a.cmd
    pos_map = {
        "job": ["job"], "apply": ["job"], "hire": ["job", "worker"], "decline": ["job", "worker"], "close-job": ["job"],
        "sign-acceptance": ["job"], "submit": ["job"], "review": ["job"], "pay": ["job", "amount"], "transfer": ["to", "amount"],
        "message": ["to"], "stake": ["amount"], "unstake": ["amount"], "set-consent": ["attester"], "attest": ["member", "amount"],
        "withdraw-backing": ["member", "amount"], "drop-attester": ["attester"], "fund-reserve": ["amount"], "remit": ["guarantee"],
        "mark-lapsed": ["guarantee"], "expire": ["guarantee"], "guarantee": ["guarantee"], "set-line": ["member", "amount"],
        "open": ["acceptance"], "reject-acceptance": ["acceptance"], "payments": ["job"], "mark-paid": ["guarantee"],
        "claim": ["guarantee"], "cancel": ["guarantee"],
    }
    names = pos_map.get(c, [])
    if len(p) < len(names):
        print(f"usage: {c} " + " ".join(n.upper() for n in names) + " [options]; run `help`")
        sys.exit(2)
    for n, v in zip(names, p):
        args[n] = v
    if c == "message" and "text" not in args and len(p) > 1:
        args["text"] = " ".join(p[1:])
    req = urllib.request.Request(URL, data=json.dumps({"me": a.me, "token": a.token, "cmd": c, "args": args}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        out = json.load(r)
    res = out["result"]
    if not out["ok"]:
        print("REFUSED:", res)
        sys.exit(1)
    if isinstance(res, str):
        print(res)
    else:
        print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
