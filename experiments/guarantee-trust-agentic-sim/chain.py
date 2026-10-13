"""Minimal GuaranteeTrust / ERC-20 chain helper (no compiled ABI needed: signatures are encoded by hand).

Used by world.py against an Anvil fork of Base Sepolia. Testnet only; no value.
"""
import threading
from eth_abi import encode, decode
from eth_account import Account
from web3 import Web3

ACCEPTANCE_T = "(address,bytes32,bytes32,uint256,uint256,bytes32,uint256,uint256,uint256,uint64,uint256,uint256)"
MEMBER_T = "(" + ",".join(["uint256"] * 10 + ["uint64"] * 8 + ["uint256"] * 2) + ")"
MEMBER_FIELDS = ["stake", "dues", "line", "backingGiven", "committedLine", "committedDues", "backingReceived",
                 "backingCommitted", "openAttestees", "unpaidContributions", "guaranteesOpened", "guaranteesPaid",
                 "claimsAsWorker", "contributionsRemitted", "contributionsLapsed", "attestationsGiven",
                 "attestationsReceived", "attesteeClaims", "contributedTotal", "backingLost"]
GUARANTEE_T = "(address,bytes32,bytes32,uint128,uint128,uint128,uint128,bytes32,uint8,bool,bool,uint64,uint64,uint64,uint128,uint128,uint128,uint128,uint64,bytes32)"
GUARANTEE_FIELDS = ["worker", "clientId", "groupId", "amount", "fromBacking", "fromLine", "fromDues", "termsHash",
                    "state", "remitted", "lapsed", "openedAt", "paidAt", "settleBy", "wage", "contributionDue",
                    "contributionBps", "contributionCap", "remitWindow", "evidenceHash"]
SCORE_T = "(" + ",".join(["uint64"] * 8 + ["uint256", "uint256", "int256"]) + ")"
SCORE_FIELDS = ["guaranteesOpened", "guaranteesPaid", "claimsAsWorker", "contributionsRemitted", "contributionsLapsed",
                "attestationsGiven", "attestationsReceived", "attesteeClaims", "contributedTotal", "backingLost", "composite"]
STATES = ["None", "Open", "Paid", "Claimed", "Cancelled", "Expired"]

ERRORS = ["NotAdjudicator()", "NotIssuer()", "NotGuardian()", "IsPaused()", "ZeroAmount()", "BadParam()",
          "InsufficientTrust()", "InsufficientCapacity()", "ExposureCap()", "GroupCap()", "ReserveFloor()",
          "ClientBlocked()", "ContributionOutstanding()", "SelfAttestation()", "NoConsent()", "AttestCap()",
          "TooManyAttesters()", "TooManyAttestees()", "BackingLocked()", "BudgetExceeded()", "LineCommitted()",
          "WrongState()", "TooEarly()", "NothingDue()", "ReleaseTooLarge()", "BadSignature()", "SignatureExpired()",
          "NonceAlreadyUsed()", "PolicyMismatch()", "BadTerm()", "PastSettleBy()", "StaleNonce()", "GroupMismatch()",
          "ZeroClient()", "SponsorCapital()", "ReleaseWhileOpen()",
          "OwnableUnauthorizedAccount(address)", "ERC20InsufficientBalance(address,uint256,uint256)",
          "ERC20InsufficientAllowance(address,uint256,uint256)", "SafeERC20FailedOperation(address)"]
ERROR_MAP = {Web3.keccak(text=e)[:4].hex(): e for e in ERRORS}

EXPLAIN = {
    "InsufficientTrust()": "not enough free stake or dues of your own to do this",
    "InsufficientCapacity()": "the worker does not have enough guarantee capacity (backing + line + dues) for this amount, or pledged too few dues",
    "ExposureCap()": "one guarantee may be at most 20% of the reserve",
    "GroupCap()": "open guarantees on this client group would exceed 30% of the reserve",
    "ReserveFloor()": "the reserve must keep twice the guarantee amount uncommitted after opening; the pool is too full right now",
    "ClientBlocked()": "this client already has an open guarantee, or this client or its group has defaulted before",
    "ContributionOutstanding()": "the worker still owes a contribution on a paid guarantee; remit it first",
    "NoConsent()": "the member has not consented to you as an attester (they must run set-consent first)",
    "AttestCap()": "backing for one member is capped at 20",
    "TooManyAttesters()": "the member already has 5 attesters",
    "TooManyAttestees()": "you already back 5 members",
    "BackingLocked()": "that backing is locked in an open guarantee",
    "BudgetExceeded()": "the issuer budget is exhausted",
    "SponsorCapital()": "lines held cannot exceed the sponsor capital in the reserve",
    "WrongState()": "the guarantee is not in the right state for this",
    "TooEarly()": "too early: the deadline or window has not passed yet",
    "NothingDue()": "nothing is due on this guarantee",
    "PastSettleBy()": "the guarantee's settle-by date has passed; it can only be expired now",
    "BadTerm()": "settle-by must be between 1 and 60 days from now",
    "NonceAlreadyUsed()": "this signed acceptance was already used or revoked",
    "ERC20InsufficientBalance(address,uint256,uint256)": "you do not have enough USDC",
}


def selector(sig):
    return Web3.keccak(text=sig)[:4]


def sig_types(sig):
    inner = sig[sig.index("(") + 1:-1]
    return split_types(inner)


def split_types(s):
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    if cur:
        out.append(cur)
    return out


class Chain:
    def __init__(self, rpc, gt, token):
        self.w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 120}))
        self.gt = Web3.to_checksum_address(gt)
        self.token = Web3.to_checksum_address(token)
        self.lock = threading.Lock()
        self.chain_id = self.w3.eth.chain_id

    # ---------------------------------------------------------------- raw
    def call(self, to, sig, args=(), outs=None, frm=None):
        data = selector(sig) + encode(sig_types(sig), list(args))
        tx = {"to": to, "data": data}
        if frm:
            tx["from"] = frm
        res = self.w3.eth.call(tx)
        if outs is None:
            return res
        vals = decode(outs, res)
        return vals[0] if len(outs) == 1 else vals

    def decode_error(self, exc):
        data = None
        if isinstance(exc.args[0], dict):
            data = exc.args[0].get("data")
        elif isinstance(exc.args[0], str) and "0x" in exc.args[0]:
            data = exc.args[0][exc.args[0].index("0x"):].split("'")[0].split('"')[0]
        if isinstance(data, dict):
            data = data.get("data")
        if isinstance(data, str) and data.startswith("0x4e487b71"):
            return "panic (probably no such guarantee id)"
        if isinstance(data, str) and data.startswith("0x") and len(data) >= 10:
            name = ERROR_MAP.get(data[2:10], data[:10])
            return name + (": " + EXPLAIN[name] if name in EXPLAIN else "")
        return str(exc)[:300]

    def send(self, key, to, sig, args=(), value=0):
        """Simulate, then sign and send; returns (receipt, error)."""
        acct = Account.from_key(key)
        data = selector(sig) + encode(sig_types(sig), list(args))
        with self.lock:
            tx = {"from": acct.address, "to": to, "data": data, "value": value, "chainId": self.chain_id}
            try:
                gas = self.w3.eth.estimate_gas(tx)
            except Exception as e:  # noqa: BLE001
                return None, self.decode_error(e)
            tx["gas"] = int(gas * 1.3) + 20000
            tx["nonce"] = self.w3.eth.get_transaction_count(acct.address, "pending")
            tx["maxFeePerGas"] = self.w3.to_wei(2, "gwei")
            tx["maxPriorityFeePerGas"] = self.w3.to_wei(1, "gwei")
            signed = acct.sign_transaction(tx)
            h = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            rc = self.w3.eth.wait_for_transaction_receipt(h, timeout=120)
        if rc.status != 1:
            return rc, "transaction reverted"
        return rc, None

    def send_as(self, frm, to, sig, args=()):
        """eth_sendTransaction from an impersonated (unlocked) account on Anvil."""
        data = selector(sig) + encode(sig_types(sig), list(args))
        with self.lock:
            self.w3.provider.make_request("anvil_impersonateAccount", [frm])
            h = self.w3.eth.send_transaction({"from": frm, "to": to, "data": data, "gas": 2_000_000})
            rc = self.w3.eth.wait_for_transaction_receipt(h, timeout=120)
        if rc.status != 1:
            raise RuntimeError("impersonated tx reverted")
        return rc

    def rpc(self, method, params):
        return self.w3.provider.make_request(method, params)

    def now(self):
        return self.w3.eth.get_block("latest").timestamp

    # ---------------------------------------------------------------- views
    def u(self, name):
        return self.call(self.gt, name + "()", (), ["uint256"])

    def summary(self):
        s = {k: self.u(k) for k in ["reserve", "outstanding", "totalStake", "totalDues", "sponsorCapital",
                                    "issuerBudget", "issuerHeld", "issuerSpent", "guaranteeCount", "maxShareBps",
                                    "maxGroupShareBps", "floorMultiple", "contributionBps", "contributionCap",
                                    "remitWindow", "lineCap", "attestCap", "maxTerm"]}
        s["tokenBalance"] = self.balance(self.gt)
        s["paused"] = self.call(self.gt, "paused()", (), ["bool"])
        return s

    def balance(self, who):
        return self.call(self.token, "balanceOf(address)", [who], ["uint256"])

    def allowance(self, who):
        return self.call(self.token, "allowance(address,address)", [who, self.gt], ["uint256"])

    def member(self, who):
        vals = self.call(self.gt, "memberOf(address)", [who], [MEMBER_T])
        return dict(zip(MEMBER_FIELDS, vals))

    def score(self, who):
        return dict(zip(SCORE_FIELDS, self.call(self.gt, "score(address)", [who], [SCORE_T])))

    def capacity(self, who):
        return self.call(self.gt, "capacity(address)", [who], ["uint256"])

    def free_to_back(self, who):
        return self.call(self.gt, "freeToBack(address)", [who], ["uint256"])

    def attesters_of(self, who):
        return list(self.call(self.gt, "attestersOf(address)", [who], ["address[]"]))

    def backing(self, att, mem):
        return self.call(self.gt, "backing(address,address)", [att, mem], ["uint256"])

    def consent(self, mem, att):
        return self.call(self.gt, "consent(address,address)", [mem, att], ["bool"])

    def guarantee(self, gid):
        g = dict(zip(GUARANTEE_FIELDS, self.call(self.gt, "guarantee(uint256)", [gid], [GUARANTEE_T])))
        g["state"] = STATES[g["state"]]
        for k in ("clientId", "groupId", "termsHash", "evidenceHash"):
            g[k] = "0x" + g[k].hex()
        return g

    def shares_of(self, gid):
        return [{"attester": a, "amount": b} for a, b in self.call(self.gt, "sharesOf(uint256)", [gid], ["(address,uint128)[]"])]

    def client_flags(self, client_id, group_id):
        return {
            "clientOpen": self.call(self.gt, "clientOpen(bytes32)", [client_id], ["bool"]),
            "clientDefaulted": self.call(self.gt, "clientDefaulted(bytes32)", [client_id], ["bool"]),
            "groupDefaulted": self.call(self.gt, "groupDefaulted(bytes32)", [group_id], ["bool"]),
            "groupExposure": self.call(self.gt, "groupExposure(bytes32)", [group_id], ["uint256"]),
        }

    def acceptance_digest(self, a):
        return self.call(self.gt, "acceptanceDigest(" + ACCEPTANCE_T + ")", [a], ["bytes32"])

    def sign_hash(self, key, digest):
        signed = Account.unsafe_sign_hash(digest, key)
        return bytes(signed.signature)

    def transfers(self, frm, to, from_block=0):
        """ERC-20 Transfer events from frm to to."""
        topic0 = Web3.keccak(text="Transfer(address,address,uint256)").hex()
        pad = lambda a: "0x" + a[2:].lower().rjust(64, "0")
        logs = self.w3.eth.get_logs({"fromBlock": from_block, "toBlock": "latest", "address": self.token,
                                     "topics": [topic0, pad(frm), pad(to)]})
        return [{"amount": int.from_bytes(l["data"], "big"), "block": l["blockNumber"], "tx": l["transactionHash"].hex()} for l in logs]
