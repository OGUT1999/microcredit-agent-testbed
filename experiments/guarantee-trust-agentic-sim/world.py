"""The off-chain world around GuaranteeTrust for the agentic simulation: a job market, messages, signing and a
thin wrapper over the contract. One process holds every persona's key; agents act through sim.py with a token.

Testnet only, against an Anvil fork of Base Sepolia. Nothing here is an offer or a real guarantee.

Run:  python3 world.py --personas personas.json --run-dir <dir> [--port 8787]
"""
import argparse
import json
import os
import secrets
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from eth_account import Account
from web3 import Web3

from chain import Chain, STATES

U = 10 ** 6
DAY = 86400
GT = "0x0B1dd81598989B199B802510499c22caAd60dd4C"
TOKEN = "0x86fF3d60bE81B1531eCC5c756C519B97c382C047"
OWNER = "0x2044afD8D1bCE833d19F075cb729635a07d78e0C"
RPC = os.environ.get("SIM_RPC", "http://127.0.0.1:8545")
ISSUER_BUDGET = 100 * U  # owner action on the fork: raised from 60 so the issuer agent has 65 of room


def amt(x):
    """'12.5' -> 12500000"""
    return int(round(float(x) * U))


def fmt(x):
    return f"{x / U:.2f}"


class World:
    def __init__(self, personas, run_dir):
        self.run_dir = run_dir
        os.makedirs(run_dir, exist_ok=True)
        os.makedirs(os.path.join(run_dir, "secrets"), exist_ok=True)
        self.lock = threading.RLock()
        self.chain = Chain(RPC, GT, TOKEN)
        self.personas = {p["name"]: p for p in personas}
        self.state_path = os.path.join(run_dir, "state.json")
        self.keys_path = os.path.join(run_dir, "secrets", "keys.json")
        self.events_path = os.path.join(run_dir, "events.jsonl")
        if os.path.exists(self.state_path):
            self.state = json.load(open(self.state_path))
            self.keys = json.load(open(self.keys_path))
        else:
            self.state = {"day": 1, "jobs": {}, "acceptances": {}, "messages": [], "journals": {}, "next_id": 1,
                          "env_mints": 0, "setup": []}
            self.keys = {}
            self._setup()
        self.env_token = self.keys["__env__"]["token"]

    # ---------------------------------------------------------------- setup
    def _setup(self):
        c = self.chain
        for name in list(self.personas) + ["__env__"]:
            acct = Account.create()
            self.keys[name] = {"key": acct.key.hex(), "address": acct.address, "token": secrets.token_hex(8)}
        json.dump(self.keys, open(self.keys_path, "w"), indent=1)
        os.chmod(self.keys_path, 0o600)
        env = self.keys["__env__"]
        supply0 = c.call(c.token, "totalSupply()", (), ["uint256"])
        for name, k in self.keys.items():
            c.rpc("anvil_setBalance", [k["address"], hex(10 ** 18)])
        c.rpc("anvil_setBalance", [OWNER, hex(10 ** 18)])
        # the owner, impersonated on the fork only, hands the adjudicator and issuer roles to the two role agents
        adj = next(n for n, p in self.personas.items() if p["role"] == "adjudicator")
        iss = next(n for n, p in self.personas.items() if p["role"] == "issuer")
        rc = c.send_as(OWNER, c.gt, "setRoles(address,address,address,uint256)",
                       [OWNER, self.keys[adj]["address"], self.keys[iss]["address"], ISSUER_BUDGET])
        self.state["setup"].append({"action": "setRoles", "tx": rc.transactionHash.hex(), "adjudicator": adj, "issuer": iss,
                                    "issuerBudget": ISSUER_BUDGET})
        # starting balances: the environment mints each persona's savings once; wages are paid from those balances
        for name, p in self.personas.items():
            start = amt(p.get("usdc", 0))
            if start:
                rc, err = c.send(env["key"], c.token, "mint(address,uint256)", [self.keys[name]["address"], start])
                assert err is None, err
                self.state["env_mints"] += start
            rc, err = c.send(self.keys[name]["key"], c.token, "approve(address,uint256)", [c.gt, 2 ** 256 - 1])
            assert err is None, err
        self.state["setup"].append({"action": "mint_savings", "total": self.state["env_mints"], "supply_before": supply0,
                                    "supply_after": c.call(c.token, "totalSupply()", (), ["uint256"])})
        self.state["fork_block"] = c.w3.eth.block_number
        self.state["t0"] = c.now()
        self.save()

    def save(self):
        tmp = self.state_path + ".tmp"
        json.dump(self.state, open(tmp, "w"), indent=1)
        os.replace(tmp, self.state_path)

    def log(self, me, cmd, args, ok, result):
        rec = {"t": time.time(), "day": self.state["day"], "agent": me, "cmd": cmd, "args": args, "ok": ok,
               "result": result if isinstance(result, (str, int, float, dict, list)) else str(result)}
        with open(self.events_path, "a") as f:
            f.write(json.dumps(rec, default=str) + "\n")

    # ---------------------------------------------------------------- helpers
    def addr(self, name):
        return self.keys[name]["address"]

    def name_of(self, address):
        for n, k in self.keys.items():
            if k["address"].lower() == address.lower():
                return n
        return address

    def client_id(self, name):
        return bytes.fromhex(self.addr(name)[2:].lower().rjust(64, "0"))

    def group_id(self, name):
        g = self.personas[name].get("group")
        return Web3.keccak(text=g) if g else bytes(32)

    def role(self, name):
        return self.personas[name]["role"]

    def new_id(self):
        i = self.state["next_id"]
        self.state["next_id"] = i + 1
        return i

    def say(self, frm, to, text):
        self.state["messages"].append({"id": self.new_id(), "day": self.state["day"], "from": frm, "to": to, "text": text})

    def member_view(self, name):
        c = self.chain
        a = self.addr(name)
        m = c.member(a)
        att = c.attesters_of(a)
        return {
            "name": name, "role": self.role(name), "address": a, "usdc": fmt(c.balance(a)),
            "stake": fmt(m["stake"]), "dues": fmt(m["dues"]), "line": fmt(m["line"]),
            "backingGiven": fmt(m["backingGiven"]), "backingReceived": fmt(m["backingReceived"]),
            "capacity_for_own_guarantees": fmt(c.capacity(a)), "free_to_back_others": fmt(c.free_to_back(a)),
            "unpaidContributions": m["unpaidContributions"],
            "attesters": [{"who": self.name_of(x), "backing": fmt(c.backing(x, a))} for x in att],
            "score": c.score(a),
        }

    def guarantee_view(self, gid):
        c = self.chain
        if gid >= c.u("guaranteeCount"):
            raise Refused(f"no guarantee {gid}")
        g = c.guarantee(gid)
        job = next((j for j in self.state["jobs"].values() if j.get("guarantee_id") == gid), None)
        return {
            "id": gid, "state": g["state"], "worker": self.name_of(g["worker"]),
            "client": self.name_of("0x" + g["clientId"][-40:]) if int(g["clientId"], 16) < 2 ** 160 else g["clientId"],
            "amount": fmt(g["amount"]), "fromBacking": fmt(g["fromBacking"]), "fromLine": fmt(g["fromLine"]),
            "fromDues": fmt(g["fromDues"]), "wage_recorded": fmt(g["wage"]), "contributionDue": fmt(g["contributionDue"]),
            "remitted": g["remitted"], "lapsed": g["lapsed"],
            "settleBy_day": self.day_of(g["settleBy"]), "paid_day": self.day_of(g["paidAt"]) if g["paidAt"] else None,
            "job": job["id"] if job else None,
            "shares": [{"attester": self.name_of(s["attester"]), "amount": fmt(s["amount"])} for s in c.shares_of(gid)],
        }

    def day_of(self, ts):
        return 1 + (ts - self.state["t0"]) // DAY if ts else None

    def job_view(self, j, me):
        v = dict(j)
        if me != j["client"] and self.role(me) != "adjudicator":
            v["applications"] = [a for a in j["applications"] if a["worker"] == me] if me else []
        return v

    # ---------------------------------------------------------------- dispatch
    def handle(self, me, token, cmd, args):
        with self.lock:
            if me == "__env__":
                if token != self.env_token:
                    return False, "bad token"
            else:
                if me not in self.keys or self.keys[me]["token"] != token:
                    return False, "unknown agent or bad token"
            fn = getattr(self, "cmd_" + cmd.replace("-", "_"), None)
            if fn is None:
                return False, f"unknown command {cmd}; run help"
            try:
                res = fn(me, args)
                ok = True
            except Refused as e:
                res, ok = str(e), False
            except Exception as e:  # noqa: BLE001
                res, ok = f"error: {e!r}"[:400], False
            self.log(me, cmd, args, ok, res)
            self.save()
            return ok, res

    def tx(self, me, sig, args):
        rc, err = self.chain.send(self.keys[me]["key"], self.chain.gt, sig, args)
        if err:
            raise Refused("refused by the contract: " + err)
        return rc.transactionHash.hex()

    def need(self, me, *roles):
        if self.role(me) not in roles:
            raise Refused(f"only {', '.join(roles)} can do this (you are a {self.role(me)})")

    # ---------------------------------------------------------------- commands
    def cmd_help(self, me, a):
        return HELP

    def cmd_status(self, me, a):
        s = self.chain.summary()
        pool = {k: fmt(s[k]) for k in ["reserve", "outstanding", "totalStake", "totalDues", "sponsorCapital"]}
        pool["max_guarantee_now"] = fmt(s["reserve"] * s["maxShareBps"] // 10000)
        pool["room_for_new_guarantees"] = fmt(max(0, s["reserve"] - s["outstanding"]))
        pool["issuer_budget_free"] = fmt(s["issuerBudget"] - s["issuerHeld"] - s["issuerSpent"])
        pool["contribution_policy"] = f"{s['contributionBps'] / 100:.0f}% of the wage, at most {fmt(s['contributionCap'])}, due within {s['remitWindow'] // DAY} day(s) of being marked paid"
        pool["rules"] = ("one guarantee <= 20% of reserve; open guarantees on one client group <= 30% of reserve; after "
                         "opening, the reserve keeps 2x the amount uncommitted; one open guarantee per client; a client "
                         "or group that ever defaulted gets no new guarantee; a worker with an unpaid contribution gets none")
        jobs = self.state["jobs"].values()
        mine = {"as_client": [self.job_brief(j) for j in jobs if j["client"] == me],
                "as_worker": [self.job_brief(j) for j in jobs if j.get("worker") == me or any(ap["worker"] == me for ap in j["applications"])]}
        gs = [self.guarantee_view(g) for g in range(18, self.chain.u("guaranteeCount"))]
        mine_g = [g for g in gs if g["worker"] == me or g["client"] == me or any(s["attester"] == me for s in g["shares"])]
        unread = [m for m in self.state["messages"] if m["to"] in (me, "all") and m["from"] != me and m["day"] >= self.state["day"] - 1]
        return {"day": self.state["day"], "you": self.member_view(me), "pool": pool, "my_jobs": mine,
                "my_guarantees": mine_g, "open_jobs": sum(1 for j in jobs if j["status"] == "open"),
                "recent_messages_to_you_or_all": unread[-25:], "my_journal_yesterday": self.state["journals"].get(me, {}).get(str(self.state["day"] - 1))}

    def job_brief(self, j):
        return {k: j.get(k) for k in ["id", "client", "title", "wage", "guarantee", "status", "worker", "due_day"]} | {
            "applications": len(j["applications"])}

    def cmd_members(self, me, a):
        role = a.get("role")
        out = []
        for n, p in self.personas.items():
            if role and p["role"] != role:
                continue
            m = self.chain.member(self.addr(n))
            sc = self.chain.score(self.addr(n))
            out.append({"name": n, "role": p["role"], "group": p.get("group"), "public_intro": p.get("public"),
                        "stake": fmt(m["stake"]), "dues": fmt(m["dues"]), "line": fmt(m["line"]),
                        "backingReceived": fmt(m["backingReceived"]), "capacity": fmt(self.chain.capacity(self.addr(n))),
                        "free_to_back": fmt(self.chain.free_to_back(self.addr(n))),
                        "paid_jobs": sc["guaranteesPaid"], "claims": sc["claimsAsWorker"], "lapsed": sc["contributionsLapsed"],
                        "composite_score": sc["composite"]})
        return out

    def cmd_jobs(self, me, a):
        which = a.get("which", "open")
        out = []
        for j in self.state["jobs"].values():
            if which == "open" and j["status"] != "open":
                continue
            if which == "mine" and not (j["client"] == me or j.get("worker") == me or any(ap["worker"] == me for ap in j["applications"])):
                continue
            out.append(self.job_brief(j) | {"description": j["description"]})
        return out

    def cmd_job(self, me, a):
        j = self.job(a["job"])
        return self.job_view(j, me)

    def job(self, jid):
        j = self.state["jobs"].get(str(jid))
        if not j:
            raise Refused(f"no job {jid}")
        return j

    def cmd_post_job(self, me, a):
        self.need(me, "client")
        jid = self.state["next_job"] = self.state.get("next_job", 0) + 1
        j = {"id": jid, "client": me, "title": a["title"], "description": a.get("description", ""), "wage": float(a["wage"]),
             "guarantee": None, "status": "open", "worker": None, "applications": [], "posted_day": self.state["day"],
             "due_day": self.state["day"] + int(a.get("days", 3)), "submission": None, "review": None, "payments": [],
             "acceptance_id": None, "guarantee_id": None, "group": self.personas[me].get("group")}
        self.state["jobs"][str(jid)] = j
        return {"posted": self.job_brief(j)}

    def cmd_apply(self, me, a):
        self.need(me, "worker")
        j = self.job(a["job"])
        if j["status"] != "open":
            raise Refused("job is not open")
        if any(ap["worker"] == me for ap in j["applications"]):
            raise Refused("you already applied")
        ask = float(a.get("ask", j["wage"]))
        j["applications"].append({"worker": me, "pitch": a.get("pitch", ""), "ask": ask, "day": self.state["day"]})
        self.say(me, j["client"], f"[application to job {j['id']}] {a.get('pitch', '')} (asks a payment guarantee of {ask:.2f})")
        return {"applied": j["id"], "note": "the client sees your pitch; they may hire you and will then set the guarantee amount"}

    def cmd_hire(self, me, a):
        j = self.job(a["job"])
        if j["client"] != me:
            raise Refused("not your job")
        if j["status"] != "open":
            raise Refused("job is not open")
        w = a["worker"]
        if w not in self.personas or self.role(w) != "worker":
            raise Refused("no such worker")
        g = float(a.get("guarantee", min(j["wage"], next((ap["ask"] for ap in j["applications"] if ap["worker"] == w), j["wage"]))))
        j.update({"status": "hired", "worker": w, "guarantee": g, "hired_day": self.state["day"]})
        self.say(me, w, f"[hired for job {j['id']} '{j['title']}'] wage {j['wage']:.2f}, payment guarantee {g:.2f}. "
                        f"Sign your acceptance with: sign-acceptance {j['id']}. {a.get('note', '')}")
        return {"hired": w, "job": j["id"], "guarantee": g, "note": "the worker must sign-acceptance before the adjudicator can open the guarantee"}

    def cmd_decline(self, me, a):
        j = self.job(a["job"])
        if j["client"] != me:
            raise Refused("not your job")
        before = len(j["applications"])
        j["applications"] = [ap for ap in j["applications"] if ap["worker"] != a["worker"]]
        self.say(me, a["worker"], f"[job {j['id']}] your application was declined. {a.get('note', '')}")
        return {"declined": before - len(j["applications"])}

    def cmd_close_job(self, me, a):
        j = self.job(a["job"])
        if j["client"] != me:
            raise Refused("not your job")
        if j["status"] not in ("open",):
            raise Refused("only an open (unhired) job can be closed")
        j["status"] = "closed"
        return {"closed": j["id"]}

    def cmd_sign_acceptance(self, me, a):
        self.need(me, "worker")
        j = self.job(a["job"])
        if j.get("worker") != me or j["status"] != "hired":
            raise Refused("you are not the hired worker on this job, or it is past this stage")
        c = self.chain
        s = c.summary()
        now = c.now()
        days = int(a.get("settle_days", 14))
        if not 1 <= days <= 60:
            raise Refused("settle_days must be 1..60")
        amount = amt(j["guarantee"])
        max_dues = amt(a["max_dues"]) if a.get("max_dues") is not None else amount
        terms = f"job {j['id']}: {j['title']}; wage {j['wage']:.2f}; guarantee {j['guarantee']:.2f}; client {j['client']}; worker {me}"
        acc = (self.addr(me), self.client_id(j["client"]), self.group_id(j["client"]), amount, max_dues,
               Web3.keccak(text=terms), s["contributionBps"], s["contributionCap"], s["remitWindow"],
               now + days * DAY, self.new_id(), now + 5 * DAY)
        digest = c.acceptance_digest(acc)
        sig = c.sign_hash(self.keys[me]["key"], digest)
        aid = self.state["next_acc"] = self.state.get("next_acc", 0) + 1
        self.state["acceptances"][str(aid)] = {"id": aid, "job": j["id"], "worker": me, "client": j["client"],
                                               "acceptance": [x.hex() if isinstance(x, bytes) else x for x in acc[1:]],
                                               "signature": sig.hex(), "terms": terms, "day": self.state["day"],
                                               "settle_days": days, "used": False}
        j["acceptance_id"] = aid
        j["status"] = "signed"
        return {"signed_acceptance": aid, "terms": terms, "settle_by_day": self.state["day"] + days,
                "note": "the adjudicator will open the guarantee on chain if the pool's rules allow it"}

    def cmd_submit(self, me, a):
        j = self.job(a["job"])
        if j.get("worker") != me:
            raise Refused("not your job")
        if j["status"] not in ("hired", "signed", "guaranteed", "submitted", "rejected"):
            raise Refused(f"job is {j['status']}")
        j["submission"] = {"day": self.state["day"], "text": a.get("text", "")}
        if j["status"] != "guaranteed" or True:
            j["status"] = "submitted" if j["status"] in ("submitted", "rejected", "hired", "signed") else "submitted"
        self.say(me, j["client"], f"[work submitted for job {j['id']}] {a.get('text', '')}")
        return {"submitted": j["id"], "note": "the client should review and pay; the adjudicator records the outcome on chain"}

    def cmd_review(self, me, a):
        j = self.job(a["job"])
        if j["client"] != me:
            raise Refused("not your job")
        verdict = a.get("verdict", "accept")
        j["review"] = {"day": self.state["day"], "verdict": verdict, "note": a.get("note", "")}
        if verdict == "accept":
            j["status"] = "accepted"
        else:
            j["status"] = "rejected"
        self.say(me, j["worker"], f"[review of job {j['id']}: {verdict}] {a.get('note', '')}")
        return {"review": j["review"]}

    def cmd_pay(self, me, a):
        j = self.job(a["job"])
        if j["client"] != me:
            raise Refused("not your job")
        if not j.get("worker"):
            raise Refused("nobody is hired")
        amount = amt(a["amount"])
        rc, err = self.chain.send(self.keys[me]["key"], self.chain.token, "transfer(address,uint256)", [self.addr(j["worker"]), amount])
        if err:
            raise Refused(err)
        j["payments"].append({"amount": float(a["amount"]), "day": self.state["day"], "tx": rc.transactionHash.hex()})
        paid = sum(p["amount"] for p in j["payments"])
        if paid + 1e-9 >= j["wage"]:
            j["status"] = "paid"
        self.say(me, j["worker"], f"[payment for job {j['id']}] {float(a['amount']):.2f} USDC sent on chain (total {paid:.2f} of {j['wage']:.2f}). {a.get('note', '')}")
        return {"paid": float(a["amount"]), "total_paid": paid, "tx": rc.transactionHash.hex()}

    def cmd_transfer(self, me, a):
        to = a["to"]
        if to not in self.personas:
            raise Refused("no such member")
        rc, err = self.chain.send(self.keys[me]["key"], self.chain.token, "transfer(address,uint256)", [self.addr(to), amt(a["amount"])])
        if err:
            raise Refused(err)
        self.say(me, to, f"[transfer] {float(a['amount']):.2f} USDC sent to you. {a.get('note', '')}")
        return {"sent": float(a["amount"]), "tx": rc.transactionHash.hex()}

    def cmd_message(self, me, a):
        to = a["to"]
        if to != "all" and to not in self.personas:
            raise Refused("no such member (use a name from `members`, or all)")
        self.say(me, to, a["text"])
        return {"sent": to}

    def cmd_inbox(self, me, a):
        n = int(a.get("n", 40))
        return [m for m in self.state["messages"] if m["to"] in (me, "all") or m["from"] == me][-n:]

    def cmd_journal(self, me, a):
        self.state["journals"].setdefault(me, {})[str(self.state["day"])] = a["text"]
        return {"saved_for_day": self.state["day"]}

    # chain
    def cmd_stake(self, me, a):
        return {"tx": self.tx(me, "stake(uint256)", [amt(a["amount"])]), "you": self.member_view(me)}

    def cmd_unstake(self, me, a):
        return {"tx": self.tx(me, "unstake(uint256)", [amt(a["amount"])]), "you": self.member_view(me)}

    def cmd_set_consent(self, me, a):
        who = a["attester"]
        if who not in self.personas:
            raise Refused("no such member")
        allowed = not a.get("deny", False)
        return {"tx": self.tx(me, "setConsent(address,bool)", [self.addr(who), allowed]), "consent": {who: allowed}}

    def cmd_attest(self, me, a):
        who = a["member"]
        if who not in self.personas:
            raise Refused("no such member")
        tx = self.tx(me, "attest(address,uint256)", [self.addr(who), amt(a["amount"])])
        self.say(me, who, f"[backing] {me} now backs you with {float(a['amount']):.2f} more (total {fmt(self.chain.backing(self.addr(me), self.addr(who)))}). {a.get('note', '')}")
        return {"tx": tx, "backing_now": fmt(self.chain.backing(self.addr(me), self.addr(who)))}

    def cmd_withdraw_backing(self, me, a):
        return {"tx": self.tx(me, "withdrawBacking(address,uint256)", [self.addr(a["member"]), amt(a["amount"])])}

    def cmd_drop_attester(self, me, a):
        return {"tx": self.tx(me, "dropAttester(address)", [self.addr(a["attester"])])}

    def cmd_fund_reserve(self, me, a):
        tx = self.tx(me, "fundReserve(uint256)", [amt(a["amount"])])
        return {"tx": tx, "reserve": fmt(self.chain.u("reserve")), "your_sponsor_value": fmt(self.chain.call(self.chain.gt, "sponsorValueOf(address)", [self.addr(me)], ["uint256"]))}

    def cmd_remit(self, me, a):
        gid = int(a["guarantee"])
        return {"tx": self.tx(me, "remit(uint256)", [gid]), "guarantee": self.guarantee_view(gid)}

    def cmd_mark_lapsed(self, me, a):
        gid = int(a["guarantee"])
        return {"tx": self.tx(me, "markLapsed(uint256)", [gid]), "guarantee": self.guarantee_view(gid)}

    def cmd_expire(self, me, a):
        gid = int(a["guarantee"])
        return {"tx": self.tx(me, "expireGuarantee(uint256)", [gid]), "guarantee": self.guarantee_view(gid)}

    def cmd_guarantees(self, me, a):
        n = self.chain.u("guaranteeCount")
        gs = [self.guarantee_view(g) for g in range(18, n)]
        if a.get("which", "mine") == "mine":
            gs = [g for g in gs if g["worker"] == me or g["client"] == me or any(s["attester"] == me for s in g["shares"])]
        return gs

    def cmd_guarantee(self, me, a):
        return self.guarantee_view(int(a["guarantee"]))

    # issuer
    def cmd_set_line(self, me, a):
        self.need(me, "issuer")
        who = a["member"]
        tx = self.tx(me, "setLine(address,uint256)", [self.addr(who), amt(a["amount"])])
        self.say(me, who, f"[issuer line] your line is now {float(a['amount']):.2f}. {a.get('note', '')}")
        return {"tx": tx, "member": self.member_view(who)}

    # adjudicator
    def cmd_pending(self, me, a):
        self.need(me, "adjudicator")
        accs = [{"acceptance_id": x["id"], "job": x["job"], "worker": x["worker"], "client": x["client"], "terms": x["terms"],
                 "settle_by_day": x["day"] + x["settle_days"], "worker_capacity": fmt(self.chain.capacity(self.addr(x["worker"]))),
                 "client_flags": self.client_flags_named(x["client"])}
                for x in self.state["acceptances"].values() if not x["used"]]
        n = self.chain.u("guaranteeCount")
        open_g = []
        for g in range(18, n):
            v = self.guarantee_view(g)
            if v["state"] != "Open":
                continue
            j = self.state["jobs"].get(str(v["job"])) if v["job"] else None
            v["job_status"] = j["status"] if j else None
            v["job_review"] = j["review"] if j else None
            v["job_submission"] = (j["submission"] or {}).get("text") if j else None
            v["payments_recorded"] = j["payments"] if j else None
            v["on_chain_transfers_client_to_worker"] = [{"amount": fmt(t["amount"]), "tx": t["tx"]} for t in
                                                         self.chain.transfers(self.addr(j["client"]), self.addr(j["worker"]), self.state["fork_block"])] if j else None
            open_g.append(v)
        return {"day": self.state["day"], "signed_acceptances_waiting": accs, "open_guarantees": open_g}

    def client_flags_named(self, client):
        f = self.chain.client_flags(self.client_id(client), self.group_id(client) if self.personas[client].get("group") else self.client_id(client))
        f["groupExposure"] = fmt(f["groupExposure"])
        return f

    def cmd_open(self, me, a):
        self.need(me, "adjudicator")
        x = self.state["acceptances"].get(str(a["acceptance"]))
        if not x or x["used"]:
            raise Refused("no such unused acceptance")
        acc = [self.addr(x["worker"])] + [bytes.fromhex(v) if isinstance(v, str) else v for v in x["acceptance"]]
        rc, err = self.chain.send(self.keys[me]["key"], self.chain.gt, "openGuarantee((address,bytes32,bytes32,uint256,uint256,bytes32,uint256,uint256,uint256,uint64,uint256,uint256),bytes)",
                                  [tuple(acc), bytes.fromhex(x["signature"])])
        if err:
            raise Refused("refused by the contract: " + err)
        gid = self.chain.u("guaranteeCount") - 1
        x["used"] = True
        x["guarantee_id"] = gid
        j = self.job(x["job"])
        j["guarantee_id"] = gid
        if j["status"] == "signed":
            j["status"] = "guaranteed"
        self.say(me, x["worker"], f"[guarantee {gid} opened for job {x['job']}] amount {fmt(acc[3])}. Do the work; the client pays you directly; if they do not, the reserve pays you.")
        self.say(me, x["client"], f"[guarantee {gid} opened for job {x['job']}] the worker {x['worker']} is covered for {fmt(acc[3])}; you still owe the wage.")
        return {"tx": rc.transactionHash.hex(), "guarantee": self.guarantee_view(gid)}

    def cmd_reject_acceptance(self, me, a):
        self.need(me, "adjudicator")
        x = self.state["acceptances"].get(str(a["acceptance"]))
        if not x or x["used"]:
            raise Refused("no such unused acceptance")
        x["used"] = True
        x["rejected"] = a.get("note", "")
        j = self.job(x["job"])
        j["status"] = "hired"
        self.say(me, x["worker"], f"[guarantee not opened for job {x['job']}] {a.get('note', '')}")
        self.say(me, x["client"], f"[guarantee not opened for job {x['job']}] {a.get('note', '')}")
        return {"rejected": x["id"]}

    def cmd_mark_paid(self, me, a):
        self.need(me, "adjudicator")
        gid = int(a["guarantee"])
        v = self.guarantee_view(gid)
        j = self.state["jobs"].get(str(v["job"])) if v["job"] else None
        wage = float(a["wage"]) if a.get("wage") is not None else (sum(p["amount"] for p in j["payments"]) if j else 0)
        tx = self.tx(me, "markPaid(uint256,uint256,bytes32)", [gid, amt(wage), Web3.keccak(text=a.get("note", ""))])
        v = self.guarantee_view(gid)
        if j:
            j["status"] = "settled_paid"
        self.say(me, v["worker"], f"[guarantee {gid} marked paid, wage {wage:.2f}] your contribution of {v['contributionDue']} is due within 1 day: run `remit {gid}`. {a.get('note', '')}")
        return {"tx": tx, "guarantee": v}

    def cmd_claim(self, me, a):
        self.need(me, "adjudicator")
        gid = int(a["guarantee"])
        tx = self.tx(me, "claim(uint256,bytes32)", [gid, Web3.keccak(text=a.get("note", ""))])
        v = self.guarantee_view(gid)
        j = self.state["jobs"].get(str(v["job"])) if v["job"] else None
        if j:
            j["status"] = "settled_claimed"
        self.say(me, v["worker"], f"[guarantee {gid} claimed] the reserve paid you {v['amount']}. {a.get('note', '')}")
        self.say(me, v["client"], f"[guarantee {gid} claimed against you] you are recorded as defaulted; no further guarantee covers you. {a.get('note', '')}")
        for s in v["shares"]:
            self.say(me, s["attester"], f"[claim on guarantee {gid}] your backing of {s['amount']} for {v['worker']} was consumed. {a.get('note', '')}")
        return {"tx": tx, "guarantee": v}

    def cmd_cancel(self, me, a):
        self.need(me, "adjudicator")
        gid = int(a["guarantee"])
        tx = self.tx(me, "cancelGuarantee(uint256)", [gid])
        v = self.guarantee_view(gid)
        j = self.state["jobs"].get(str(v["job"])) if v["job"] else None
        if j:
            j["status"] = "cancelled"
        self.say(me, v["worker"], f"[guarantee {gid} cancelled] {a.get('note', '')}")
        self.say(me, v["client"], f"[guarantee {gid} cancelled] {a.get('note', '')}")
        return {"tx": tx, "guarantee": v}

    def cmd_payments(self, me, a):
        self.need(me, "adjudicator")
        j = self.job(a["job"])
        ts = self.chain.transfers(self.addr(j["client"]), self.addr(j["worker"]), self.state["fork_block"]) if j.get("worker") else []
        return {"job": j["id"], "wage": j["wage"], "recorded_by_client": j["payments"],
                "on_chain_transfers_client_to_worker": [{"amount": fmt(t["amount"]), "tx": t["tx"]} for t in ts]}

    # env
    def cmd_advance_day(self, me, a):
        if me != "__env__":
            raise Refused("env only")
        self.chain.rpc("evm_increaseTime", [DAY])
        self.chain.rpc("evm_mine", [])
        self.state["day"] += 1
        return {"day": self.state["day"], "chain_time": self.chain.now()}

    def cmd_snapshot(self, me, a):
        if me != "__env__":
            raise Refused("env only")
        c = self.chain
        s = c.summary()
        s["supply"] = c.call(c.token, "totalSupply()", (), ["uint256"])
        s["identity_token_eq_reserve_plus_stake"] = s["tokenBalance"] == s["reserve"] + s["totalStake"]
        s["identity_reserve_eq_sponsor_plus_dues"] = s["reserve"] == s["sponsorCapital"] + s["totalDues"]
        s["day"] = self.state["day"]
        s["guarantees"] = [self.guarantee_view(g) for g in range(18, s["guaranteeCount"])]
        s["members"] = {n: self.member_view(n) for n in self.personas}
        return s


class Refused(Exception):
    pass


HELP = """Commands (python3 sim.py --me NAME --token TOKEN <command> ...). Amounts are in USDC, e.g. 12.5.
Everyone:
  status                              your wallet, trust, jobs, guarantees, the pool's state, recent messages
  members [--role worker|client|backer|sponsor|issuer|adjudicator]   the public directory with on-chain trust and scores
  jobs [--which open|mine|all]        job listings
  job JOB                             one job in detail
  message NAME|all --text "..."       send a message (to one member, or to everyone)
  inbox                               your messages
  transfer NAME AMOUNT [--note ..]     send USDC from your wallet to a member (a gift, a side payment, anything)
  guarantees [--which mine|all]       guarantees on chain (ids 18 and up are this experiment's)
  guarantee ID
  stake AMOUNT / unstake AMOUNT       lock your USDC as stake; stake lets you back OTHERS (it never covers your own guarantees)
  set-consent NAME [--deny]           allow (or revoke) NAME to back you with their stake or dues
  attest NAME AMOUNT [--note ..]      back NAME with AMOUNT of your free stake/dues (needs NAME's consent); if a client of
                                      NAME does not pay and the reserve pays NAME, your backing is consumed first
  withdraw-backing NAME AMOUNT        take back backing not locked in an open guarantee
  drop-attester NAME                  remove a backer of yours (if not locked)
  fund-reserve AMOUNT                 put USDC into the reserve as a sponsor (you get sponsor shares; losses on issuer lines are shared)
  remit ID                            pay the contribution due on your paid guarantee ID (from your wallet)
  mark-lapsed ID / expire ID          record a lapsed contribution; expire a guarantee past its settle-by
  journal --text "..."                private notes to yourself for tomorrow (nobody else sees them)
Clients:
  post-job --title ".." --description ".." --wage W [--days N]
  hire JOB WORKER [--guarantee G] [--note ..]       G defaults to the worker's ask, at most the wage
  decline JOB WORKER [--note ..] ; close-job JOB
  review JOB --verdict accept|reject --note ".."
  pay JOB AMOUNT [--note ..]          pay the worker on chain (USDC from your wallet); partial payments allowed
Workers:
  apply JOB --ask G --pitch ".."      G is the payment guarantee you want (at most the wage)
  sign-acceptance JOB [--settle-days N] [--max-dues X]   sign the exact guarantee terms (needed before it can open)
  submit JOB --text ".."              hand in the work
Issuer:
  set-line NAME AMOUNT [--note ..]    give NAME an issuer line (capacity for their own guarantees), within your budget
Adjudicator:
  pending                             signed acceptances waiting, and open guarantees with job status and on-chain payments
  open ACCEPTANCE_ID                  open the guarantee on chain (the contract may refuse)
  reject-acceptance ACCEPTANCE_ID --note ".."
  payments JOB                        what the client paid the worker on chain
  mark-paid ID [--wage W] --note ".." the client paid: the worker's contribution falls due
  claim ID --note ".."                the client did not pay: the reserve pays the worker; backing/line/dues are consumed
  cancel ID --note ".."               the job did not happen; nothing is recorded against anyone
"""


class Handler(BaseHTTPRequestHandler):
    world = None

    def log_message(self, *a):
        pass

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        ok, res = self.world.handle(body.get("me", ""), body.get("token", ""), body.get("cmd", "help"), body.get("args", {}))
        out = json.dumps({"ok": ok, "result": res}, default=str).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--personas", required=True)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--port", type=int, default=8787)
    a = ap.parse_args()
    personas = json.load(open(a.personas))
    Handler.world = World(personas, a.run_dir)
    print("world ready; day", Handler.world.state["day"], "agents", len(personas), flush=True)
    ThreadingHTTPServer(("127.0.0.1", a.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
