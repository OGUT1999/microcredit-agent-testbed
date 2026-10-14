#!/usr/bin/env python3
"""Offline source-five receipt consistency, not authenticated recovery or authority.

No RPC, signer, credential, transaction, private input echo, or financial action.
Only the existing Base Sepolia RETURN then original-lender REDEPOSIT is supported.
"""
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.record_input import read_record, _unique_object

CHAIN = 84532
TOKEN = "0x036cbd53842c5426634e7929541ec2318f3dcf7e"
POOL = "0x73872b8fb7f1771c67911f03edc75abdc9514973"
AMOUNT = 5_000_000
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
DEPOSITED = "0x73a19dd210f1a7f902193214c0ee91dd35ee5b4d920cba8d519eca65a7b488ca"
BALANCES = ("source_funder_usdc", "original_lender_usdc", "root_treasury_usdc", "pool_cash", "pool_assets",
            "original_lender_shares", "source_funder_shares", "total_shares",
            "lent_principal", "impaired_principal", "queued_withdrawals")
TOP = {"schema_version", "evidence_kind", "binding", "before", "after",
       "canonical_blocks", "return_transaction", "return_receipt",
       "deposit_transaction", "deposit_receipt"}


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def obj(value, label):
    require(type(value) is dict, label + ": expected object")
    return value


def uint(value, label):
    require(type(value) is int and 0 <= value < 2**256, label + ": expected uint256 integer")
    return value


def data(value, size, label):
    require(type(value) is str and re.fullmatch(r"0x[0-9a-fA-F]{" + str(size * 2) + "}", value),
            label + ": invalid hex data width")
    return value.lower()


def address(value, label):
    result = data(value, 20, label)
    require(int(result, 16) != 0, label + ": zero address")
    return result


def quantity(value, label):
    require(type(value) is str and re.fullmatch(r"0x(?:0|[1-9a-fA-F][0-9a-fA-F]{0,63})", value),
            label + ": invalid RPC quantity")
    return int(value, 16)


def snapshot(value, label, blocks):
    value = obj(value, label)
    require(set(value) == set(BALANCES) | {"block_number", "block_hash"}, label + ": fields incomplete/unsupported")
    for key in BALANCES + ("block_number",):
        uint(value[key], label + "." + key)
    h = data(value["block_hash"], 32, label + ".block_hash")
    require(blocks.get(str(value["block_number"])) == h, label + ": unbound block hash")
    return value


def receipt(tx, value, label, sender, target, blocks):
    tx, value = obj(tx, label + " transaction"), obj(value, label + " receipt")
    tx_hash = data(value.get("transactionHash"), 32, label + " hash")
    block = quantity(value.get("blockNumber"), label + " block")
    block_hash = data(value.get("blockHash"), 32, label + " block hash")
    index = quantity(value.get("transactionIndex"), label + " index")
    require(quantity(value.get("status"), label + " status") == 1, label + ": reverted")
    require(blocks.get(str(block)) == block_hash, label + ": unbound canonical block")
    for row in (tx, value):
        require(address(row.get("from"), label + " from") == sender, label + ": wrong sender")
        require(address(row.get("to"), label + " to") == target, label + ": wrong destination")
        require(data(row.get("blockHash"), 32, label + " block hash") == block_hash,
                label + ": transaction/receipt block mismatch")
        require(quantity(row.get("blockNumber"), label + " block") == block,
                label + ": transaction/receipt height mismatch")
        require(quantity(row.get("transactionIndex"), label + " index") == index,
                label + ": transaction/receipt index mismatch")
    require(data(tx.get("hash"), 32, label + " transaction hash") == tx_hash, label + ": hash mismatch")
    require(quantity(tx.get("chainId"), label + " chain") == CHAIN, label + ": wrong chain")
    require(quantity(tx.get("value"), label + " ETH value") == 0, label + ": unexpected ETH value")
    logs = value.get("logs")
    require(type(logs) is list and 1 <= len(logs) <= 100, label + ": missing/excess logs")
    seen = set()
    for log in logs:
        obj(log, label + " log")
        require(log.get("removed") is False, label + ": removed/unknown log")
        require(data(log.get("transactionHash"), 32, label + " log hash") == tx_hash,
                label + ": foreign transaction log")
        require(data(log.get("blockHash"), 32, label + " log block") == block_hash,
                label + ": foreign block log")
        require(quantity(log.get("blockNumber"), label + " log height") == block and
                quantity(log.get("transactionIndex"), label + " log index") == index,
                label + ": foreign log position")
        log_index = quantity(log.get("logIndex"), label + " log index")
        require(log_index not in seen, label + ": duplicate log index")
        seen.add(log_index)
        address(log.get("address"), label + " log address")
        require(type(log.get("topics")) is list and len(log["topics"]) <= 4, label + ": malformed topics")
        for topic in log["topics"]:
            data(topic, 32, label + " topic")
        require(type(log.get("data")) is str and
                re.fullmatch(r"0x(?:[0-9a-fA-F]{2}){0,4096}", log["data"]), label + ": malformed log data")
    return (block, index), tx_hash, logs


def indexed(address_value):
    return "0x" + "0" * 24 + address_value[2:]


def event(logs, emitter, topics, words, label):
    matches = [log for log in logs if log["address"].lower() == emitter and
               [t.lower() for t in log["topics"]] == topics]
    require(len(matches) == 1, label + ": missing/ambiguous event")
    raw = data(matches[0]["data"], 32 * words, label + " data")[2:]
    return (tuple(int(raw[i:i + 64], 16) for i in range(0, len(raw), 64)),
            quantity(matches[0]["logIndex"], label + " log index"))


def classify(packet):
    """Check supplied records only; even a ready result is not recovery proof."""
    result = {"state": "NOT_ESTABLISHED", "recovery_verified": False,
              "human_earnings_established": False, "transaction_authorized": False,
              "gaps": [], "limitations": ["Supplied RPC records and role binding are unauthenticated.",
              "Independently reread original authority, deployed runtime/token and canonical blocks, transactions, receipts and snapshots; require chain-specific finality.",
              "This narrow source-five check does not complete three communities, all actor teardown, gas accounting or human benefit."]}
    try:
        packet = obj(packet, "packet")
        require(not set(packet) - TOP, "packet: unsupported fields")
        require(type(packet.get("schema_version")) is int and packet["schema_version"] == 1, "unsupported schema")
        require(packet.get("evidence_kind") in ("synthetic", "testnet"), "unsupported evidence kind")
        binding = obj(packet.get("binding"), "binding")
        require(set(binding) == {"chain_id", "token", "pool", "source_funder", "original_lender", "root_treasury"},
                "binding: fields incomplete/unsupported")
        require(uint(binding["chain_id"], "chain") == CHAIN, "binding: wrong chain")
        require(address(binding["token"], "token") == TOKEN and address(binding["pool"], "pool") == POOL,
                "binding: wrong deployment")
        funder, lender, treasury = [address(binding[k], k) for k in ("source_funder", "original_lender", "root_treasury")]
        require(len({funder, lender, treasury, TOKEN, POOL}) == 5, "binding: aliased roles")
        blocks = obj(packet.get("canonical_blocks"), "canonical_blocks")
        require(1 <= len(blocks) <= 20, "canonical_blocks: invalid size")
        for height, h in blocks.items():
            require(type(height) is str and re.fullmatch(r"(?:0|[1-9][0-9]{0,19})", height), "invalid block key")
            data(h, 32, "canonical block hash")
        blocks = {k: v.lower() for k, v in blocks.items()}
        before = snapshot(packet.get("before"), "before", blocks)
        after = snapshot(packet.get("after"), "after", blocks)
        for state, cash in ((before, 15_000_000), (after, 20_000_000)):
            require(state["pool_cash"] == state["pool_assets"] == cash, "pool: wrong restored assets/cash")
            require(state["root_treasury_usdc"] == 15_000_000, "root principal changed")
            require(state["source_funder_shares"] == 0 and
                    state["original_lender_shares"] == state["total_shares"] > 0, "original lender ownership not restored")
            require(all(state[k] == 0 for k in ("lent_principal", "impaired_principal", "queued_withdrawals")),
                    "pool: outstanding financial position")
        require(before["source_funder_usdc"] == AMOUNT and after["source_funder_usdc"] == 0,
                "source allocation not exactly returned")
        require(before["original_lender_usdc"] == after["original_lender_usdc"] == 0,
                "original source wallet not cleared")
        missing = [k for k in ("return_transaction", "return_receipt", "deposit_transaction", "deposit_receipt")
                   if packet.get(k) is None]
        if missing:
            result["gaps"] = ["missing " + k for k in missing]
            return result
        r_pos, r_hash, r_logs = receipt(packet["return_transaction"], packet["return_receipt"],
                                      "return", funder, TOKEN, blocks)
        d_pos, d_hash, d_logs = receipt(packet["deposit_transaction"], packet["deposit_receipt"],
                                      "deposit", lender, POOL, blocks)
        require(r_hash != d_hash, "return/deposit: duplicate transaction")
        amount_word = f"{AMOUNT:064x}"
        require(data(packet["return_transaction"].get("input"), 68, "return calldata") ==
                "0xa9059cbb" + indexed(lender)[2:] + amount_word, "return: unexpected calldata")
        require(data(packet["deposit_transaction"].get("input"), 36, "deposit calldata") ==
                "0x3b76594d" + amount_word, "deposit: unexpected calldata")
        require(before["block_number"] < r_pos[0] and r_pos < d_pos and d_pos[0] <= after["block_number"],
                "return/deposit: invalid observation/order window")
        if r_pos[0] == d_pos[0]:
            require(packet["return_receipt"]["blockHash"].lower() == packet["deposit_receipt"]["blockHash"].lower(),
                    "return/deposit: same-height hash disagreement")
            require(max(quantity(x["logIndex"], "return log index") for x in r_logs) <
                    min(quantity(x["logIndex"], "deposit log index") for x in d_logs),
                    "return/deposit: overlapping block log positions")
        returned, _ = event(r_logs, TOKEN, [TRANSFER, indexed(funder), indexed(lender)], 1, "return Transfer")
        deposited, transfer_index = event(d_logs, TOKEN, [TRANSFER, indexed(lender), indexed(POOL)], 1, "deposit Transfer")
        (assets, shares), mint_index = event(d_logs, POOL, [DEPOSITED, indexed(lender)], 2, "original-lender Deposited")
        require(returned == (AMOUNT,) and deposited == (AMOUNT,), "return/deposit: wrong amount")
        for logs in (r_logs, d_logs):
            require(sum(x["address"].lower() == TOKEN and bool(x["topics"]) and x["topics"][0].lower() == TRANSFER
                        for x in logs) == 1, "unexpected extra token movement")
        require(not any(x["address"].lower() == POOL and x["topics"] and x["topics"][0].lower() == DEPOSITED
                        for x in r_logs), "unexpected share-credit event in return")
        require(sum(x["address"].lower() == POOL and bool(x["topics"]) and x["topics"][0].lower() == DEPOSITED
                    for x in d_logs) == 1, "unexpected extra share-credit event")
        require(transfer_index < mint_index, "deposit: share event precedes token pull")
        require(assets == AMOUNT and shares > 0 and
                after["original_lender_shares"] - before["original_lender_shares"] == shares and
                after["total_shares"] - before["total_shares"] == shares, "deposit: share/assets delta mismatch")
        result["state"] = "READY_FOR_CHAIN_REVIEW"
    except (ValueError, TypeError, KeyError) as error:
        result["state"] = "INVALID_PACKET"
        result["gaps"] = [str(error)]
    return result


def unique_object(pairs):
    """Legacy decoder hook forwards to the one maintained bounded reader."""
    return _unique_object(pairs)


def main(argv=None):
    try:
        packet = read_record(argv, prog="source_recovery_gate.py", description=__doc__,
                             argument_name="packet")
        result = classify(packet)
    except (OSError, UnicodeError, ValueError, TypeError, RecursionError):
        result = {"state": "INVALID_PACKET", "recovery_verified": False,
                  "human_earnings_established": False, "transaction_authorized": False,
                  "gaps": ["unreadable or invalid JSON packet"]}
    print(json.dumps(result, sort_keys=True))
    return 0 if result["state"] == "READY_FOR_CHAIN_REVIEW" else 1


if __name__ == "__main__":
    raise SystemExit(main())
