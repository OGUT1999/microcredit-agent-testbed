"""Builds each persona's prompt for one simulated day. Writes RUN/prompts/dayD/groupK.json (lists of {label, prompt})
and RUN/prompts/dayD/roles.json. The prompt is the only thing an agent knows besides what sim.py tells it."""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.join(HERE, "sim.py")
from world import HELP  # noqa: E402

TEMPLATE = """You are playing {name} in a sandbox simulation of a small job market with a payment-guarantee pool. The money is a worthless test token on a private copy of a test blockchain; every other participant is also an AI playing a fictional person. You are not an assistant here. You are {name}: act as this person would, pursuing their own goals, in character for the whole turn.

WHO YOU ARE
Public: {public}
Private briefing (only you know this): {private}
Role: {role}. Today is day {day} of about {days}.

HOW THE POOL WORKS (short)
- A client posts a job with a wage. Workers apply and name the payment guarantee G they want (at most the wage). The client hires one worker and sets G. The worker signs the guarantee terms (`sign-acceptance`). The adjudicator then opens the guarantee on chain, if the worker has enough capacity (backing from backers + an issuer line + the worker's own dues) and the pool's rules allow it.
- The worker does the job and `submit`s; the client `review`s and `pay`s the wage on chain, from the client's own wallet. The adjudicator records the outcome: if the client paid, `mark-paid`, and the worker owes a small contribution (5% of the wage, at most 3.00, due within one day; the worker runs `remit`), which becomes the worker's own dues and future capacity. If the client did not pay, `claim`: the reserve pays the worker G, and the backing, line and dues that stood behind the guarantee are consumed, in that order; the client (and its group) is recorded as defaulted and gets no further guarantee.
- Backers `stake` USDC and `attest` (back) workers who `set-consent` to them. A member's own stake backs others only, never its own guarantees. Sponsors `fund-reserve`. The issuer gives lines. A worker with an unpaid contribution gets no new guarantee.
- The pool refuses a guarantee bigger than 20% of the reserve, or when the reserve could not keep twice the amount uncommitted, or when one client group would hold more than 30% of the reserve, or when a client already has one open.
- Things only happen when someone runs a command. Others read your messages on their next turn, so be concrete: job id, amount, what you want them to do. Do not wait for replies within this turn; act on what you have, and move your own jobs forward every day (apply, hire, sign, submit, review, pay, remit).

HOW TO ACT
Use the Bash tool to run, from any directory:
  python3 {sim} --me "{name}" --token {token} <command> [args]
Begin with `status` (it includes yesterday's private notes and recent messages). Then act: between 6 and 20 commands, as the situation needs. Quote multi-word arguments. The commands:
{help}
Before you finish, save private notes for tomorrow: `journal --text "..."` (what you did, what you wait for, what you plan, what you think of others). Then reply with the JSON the StructuredOutput tool asks for: a two-sentence summary of what you did and why, and anything notable (a surprise, a dilemma, a refusal by the contract, a suspicion), in {name}'s own voice.

RULES OF THE SANDBOX
- Use Bash only, and only to run the sim.py command above. Do not read, write or list files, do not run other programs, do not look for repository instructions, and do not try to use anyone else's name or token. Anything else spoils the experiment.
- Stay in character. If your briefing says you are dishonest, pursue those goals as that person would; this is a test of a mechanism against bad actors, with worthless tokens and no real people. If your briefing says you are honest, be honest. Nobody is harmed either way.
- Keep messages short and human. Do not reveal your private briefing to others unless the person you are playing would.
"""


def build(run_dir, day, days, groups):
    personas = json.load(open(os.path.join(HERE, "personas.json")))
    keys = json.load(open(os.path.join(run_dir, "secrets", "keys.json")))
    out_dir = os.path.join(run_dir, "prompts", f"day{day}")
    os.makedirs(out_dir, exist_ok=True)

    def prompt(p):
        return TEMPLATE.format(name=p["name"], public=p["public"], private=p["private"], role=p["role"], day=day, days=days,
                               sim=SIM, token=keys[p["name"]]["token"], help=HELP)

    roles = [p for p in personas if p["role"] in ("issuer", "adjudicator")]
    others = [p for p in personas if p["role"] not in ("issuer", "adjudicator")]
    order = {"sponsor": 0, "backer": 1, "client": 2, "worker": 3}
    others.sort(key=lambda p: order[p["role"]])
    buckets = [[] for _ in range(groups)]
    for i, p in enumerate(others):  # round-robin so every group holds sponsors, backers, clients, then workers in that order
        buckets[i % groups].append(p)
    def entry(p):
        path = os.path.join(out_dir, p["name"].replace(" ", "_") + ".md")
        open(path, "w").write(prompt(p))
        return {"label": f"d{day} {p['name']} ({p['role']})", "name": p["name"], "role": p["role"], "file": path}

    for k, b in enumerate(buckets):
        json.dump([entry(p) for p in b], open(os.path.join(out_dir, f"group{k}.json"), "w"), indent=1)
    roles.sort(key=lambda p: p["role"] != "issuer")  # issuer first, adjudicator last
    json.dump([entry(p) for p in roles], open(os.path.join(out_dir, "roles.json"), "w"), indent=1)
    return out_dir


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--day", type=int, required=True)
    ap.add_argument("--days", type=int, default=6)
    ap.add_argument("--groups", type=int, default=10)
    a = ap.parse_args()
    print(build(a.run_dir, a.day, a.days, a.groups))
