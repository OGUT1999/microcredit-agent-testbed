"""Synthetic offline regression records; no actual recovery, RPC or signer."""
import copy
import io
import json
from contextlib import redirect_stdout
import unittest
from unittest.mock import patch

import source_recovery_gate as g

FUNDER, LENDER, TREASURY = ("0x" + str(n) * 40 for n in (1, 2, 3))


def word(n):
    return f"{n:064x}"


def log(emitter, topics, values, tx, block, index, log_index):
    return {"address": emitter, "topics": topics, "data": "0x" + "".join(word(v) for v in values),
            "transactionHash": tx, "blockNumber": hex(block), "blockHash": "0x" + word(block),
            "transactionIndex": hex(index), "logIndex": hex(log_index), "removed": False}


def synthetic_ready():
    binding = {"chain_id": g.CHAIN, "token": g.TOKEN, "pool": g.POOL,
               "source_funder": FUNDER, "original_lender": LENDER, "root_treasury": TREASURY}
    before = dict.fromkeys(g.BALANCES, 0)
    before.update(block_number=100, block_hash="0x" + word(100), source_funder_usdc=g.AMOUNT,
                  root_treasury_usdc=15_000_000, pool_cash=15_000_000, pool_assets=15_000_000,
                  original_lender_shares=15_000_000_000_000, total_shares=15_000_000_000_000)
    after = dict(before, block_number=102, block_hash="0x" + word(102), source_funder_usdc=0,
                 pool_cash=20_000_000, pool_assets=20_000_000,
                 original_lender_shares=20_000_000_000_000, total_shares=20_000_000_000_000)
    packet = {"schema_version": 1, "evidence_kind": "synthetic", "binding": binding,
              "canonical_blocks": {str(b): "0x" + word(b) for b in (100, 101, 102)},
              "before": before, "after": after}
    for name, sender, target, block, tx in (("return", FUNDER, g.TOKEN, 101, "0x" + word(501)),
                                           ("deposit", LENDER, g.POOL, 102, "0x" + word(502))):
        receipt = {"from": sender, "to": target, "transactionHash": tx, "blockNumber": hex(block),
                   "blockHash": "0x" + word(block), "transactionIndex": "0x0", "status": "0x1"}
        if name == "return":
            logs = [log(g.TOKEN, [g.TRANSFER, g.indexed(FUNDER), g.indexed(LENDER)],
                        [g.AMOUNT], tx, block, 0, 0)]
        else:
            logs = [log(g.TOKEN, [g.TRANSFER, g.indexed(LENDER), g.indexed(g.POOL)],
                        [g.AMOUNT], tx, block, 0, 0),
                    log(g.POOL, [g.DEPOSITED, g.indexed(LENDER)],
                        [g.AMOUNT, 5_000_000_000_000], tx, block, 0, 1)]
        receipt["logs"] = logs
        transaction = {k: v for k, v in receipt.items() if k not in ("logs", "status", "transactionHash")}
        transaction.update(hash=tx, chainId=hex(g.CHAIN), value="0x0")
        transaction["input"] = ("0xa9059cbb" + g.indexed(LENDER)[2:] + word(g.AMOUNT) if name == "return"
                                else "0x3b76594d" + word(g.AMOUNT))
        packet[name + "_receipt"], packet[name + "_transaction"] = receipt, transaction
    return packet


class RecoveryGate(unittest.TestCase):
    def setUp(self):
        self.p = synthetic_ready()

    def invalid(self, packet=None):
        result = g.classify(self.p if packet is None else packet)
        self.assertEqual(result["state"], "INVALID_PACKET")
        self.assertFalse(result["recovery_verified"])
        self.assertFalse(result["transaction_authorized"])

    def test_ready_is_consistency_only_and_does_not_mutate(self):
        before = copy.deepcopy(self.p)
        r = g.classify(self.p)
        self.assertEqual(r["state"], "READY_FOR_CHAIN_REVIEW")
        self.assertFalse(r["recovery_verified"])
        self.assertFalse(r["human_earnings_established"])
        self.assertFalse(r["transaction_authorized"])
        self.assertEqual(self.p, before)

    def test_pool_balance_alone_is_not_ready(self):
        for key in ("return_receipt", "return_transaction", "deposit_receipt", "deposit_transaction"):
            self.p[key] = None
        self.assertEqual(g.classify(self.p)["state"], "NOT_ESTABLISHED")

    def test_direct_funder_deposit_cannot_restore_original_lender(self):
        self.p["deposit_receipt"]["from"] = FUNDER
        self.p["deposit_transaction"]["from"] = FUNDER
        self.invalid()

    def test_pool_twenty_but_wrong_share_owner(self):
        self.p["after"]["source_funder_shares"] = 5_000_000_000_000
        self.p["after"]["original_lender_shares"] -= 5_000_000_000_000
        self.invalid()

    def test_removed_or_unknown_removal_flag(self):
        for flag in (True, None, 0, "false"):
            with self.subTest(flag=flag):
                self.p["return_receipt"]["logs"][0]["removed"] = flag
                self.invalid()

    def test_failed_receipt_or_noncanonical_quantity(self):
        for status in ("0x0", 1, True, "0x01", "0x", "1"):
            with self.subTest(status=status):
                self.p["return_receipt"]["status"] = status
                self.invalid()

    def test_receipt_transaction_hash_mismatch(self):
        self.p["return_transaction"]["hash"] = "0x" + word(999)
        self.invalid()

    def test_foreign_transaction_or_block_log(self):
        for key in ("transactionHash", "blockHash"):
            with self.subTest(key=key):
                p = copy.deepcopy(self.p)
                p["return_receipt"]["logs"][0][key] = "0x" + word(999)
                self.invalid(p)

    def test_wrong_chain_and_deployment(self):
        for n in (1, 31337, True, "84532"):
            p = copy.deepcopy(self.p)
            p["binding"]["chain_id"] = n
            self.invalid(p)
        self.p["deposit_transaction"]["chainId"] = "0x1"
        self.invalid()

    def test_wrong_token_pool_recipient_or_amount(self):
        for path, value in (("address", LENDER), ("data", "0x" + word(4_999_999))):
            p = copy.deepcopy(self.p)
            p["return_receipt"]["logs"][0][path] = value
            self.invalid(p)
        self.p["return_receipt"]["logs"][0]["topics"][2] = g.indexed(TREASURY)
        self.invalid()

    def test_plain_pool_transfer_without_share_mint_rejected(self):
        self.p["deposit_receipt"]["logs"].pop()
        self.invalid()

    def test_deposit_event_credits_wrong_lender(self):
        self.p["deposit_receipt"]["logs"][1]["topics"][1] = g.indexed(FUNDER)
        self.invalid()

    def test_share_delta_and_assets_event_checked(self):
        for raw in ([g.AMOUNT, 1], [g.AMOUNT, 0], [g.AMOUNT + 1, 5_000_000_000_000]):
            self.p["deposit_receipt"]["logs"][1]["data"] = "0x" + "".join(word(n) for n in raw)
            self.invalid()

    def test_wrong_order_or_snapshot_window(self):
        self.p["before"]["block_number"] = 101
        self.p["before"]["block_hash"] = "0x" + word(101)
        self.invalid()

    def test_duplicate_or_ambiguous_logs(self):
        self.p["return_receipt"]["logs"].append(copy.deepcopy(self.p["return_receipt"]["logs"][0]))
        self.invalid()
        self.p["return_receipt"]["logs"][1]["logIndex"] = "0x1"
        self.invalid()

    def test_same_block_return_then_deposit_supported(self):
        tx, receipt = self.p["deposit_transaction"], self.p["deposit_receipt"]
        for row in [tx, receipt] + receipt["logs"]:
            row.update(blockNumber="0x65", blockHash="0x" + word(101), transactionIndex="0x1")
        for i, row in enumerate(receipt["logs"], 1):
            row["logIndex"] = hex(i)
        self.assertEqual(g.classify(self.p)["state"], "READY_FOR_CHAIN_REVIEW")
        for row in [tx, receipt] + receipt["logs"]:
            row["transactionIndex"] = "0x0"
        self.invalid()

    def test_same_block_global_log_positions_cannot_overlap(self):
        tx, receipt = self.p["deposit_transaction"], self.p["deposit_receipt"]
        for row in [tx, receipt] + receipt["logs"]:
            row.update(blockNumber="0x65", blockHash="0x" + word(101), transactionIndex="0x1")
        self.invalid()

    def test_token_pull_must_precede_share_credit_event(self):
        logs = self.p["deposit_receipt"]["logs"]
        logs[0]["logIndex"], logs[1]["logIndex"] = "0x1", "0x0"
        self.invalid()

    def test_cli_duplicate_keys_rejected_without_echo(self):
        raw = json.dumps(self.p).replace('"schema_version": 1', '"schema_version": 2, "schema_version": 1')
        with patch.object(g.Path, "read_text", return_value=raw), redirect_stdout(io.StringIO()) as out:
            self.assertEqual(g.main(["private.json"]), 1)
        self.assertEqual(json.loads(out.getvalue())["state"], "INVALID_PACKET")

    def test_approval_meta_or_wrong_amount_calldata_rejected(self):
        for name, raw in (("return", "0x095ea7b3" + g.indexed(LENDER)[2:] + word(g.AMOUNT)),
                          ("return", "0xa9059cbb" + g.indexed(LENDER)[2:] + word(g.AMOUNT - 1)),
                          ("deposit", "0x00000000" + word(g.AMOUNT)),
                          ("deposit", "0x3b76594d" + word(g.AMOUNT + 1))):
            p = copy.deepcopy(self.p)
            p[name + "_transaction"]["input"] = raw
            self.invalid(p)

    def test_extra_token_movement_cannot_hide_in_receipt(self):
        logs = self.p["return_receipt"]["logs"]
        extra = copy.deepcopy(logs[0])
        extra["logIndex"] = "0x1"
        extra["topics"][2] = g.indexed(TREASURY)
        logs.append(extra)
        self.invalid()

    def test_original_source_wallet_must_be_cleared(self):
        self.p["after"]["original_lender_usdc"] = g.AMOUNT
        self.invalid()

    def test_extra_share_credit_in_return_cannot_be_ignored(self):
        r = self.p["return_receipt"]
        r["logs"].append(log(g.POOL, [g.DEPOSITED, g.indexed(TREASURY)], [g.AMOUNT, 1],
                             r["transactionHash"], 101, 0, 1))
        self.invalid()

    def test_snapshot_hash_not_canonical(self):
        self.p["after"]["block_hash"] = "0x" + word(999)
        self.invalid()

    def test_rpc_block_reference_mismatch(self):
        self.p["return_transaction"]["blockHash"] = "0x" + word(999)
        self.invalid()

    def test_schema_and_balances_reject_booleans_floats_strings(self):
        for value in (True, 0.0, "0", -1, 2**256):
            p = copy.deepcopy(self.p)
            p["after"]["source_funder_shares"] = value
            self.invalid(p)
        self.p["schema_version"] = True
        self.invalid()

    def test_changed_root_principal_or_uncleared_positions(self):
        for field in ("root_treasury_usdc", "lent_principal", "impaired_principal", "queued_withdrawals"):
            p = copy.deepcopy(self.p)
            p["after"][field] += 1
            self.invalid(p)

    def test_role_alias_and_unknown_fields_rejected(self):
        self.p["binding"]["original_lender"] = FUNDER
        self.invalid()
        p = synthetic_ready()
        p["secret"] = "PRIVATE_SENTINEL"
        r = g.classify(p)
        self.assertEqual(r["state"], "INVALID_PACKET")
        self.assertNotIn("PRIVATE_SENTINEL", json.dumps(r))

    def test_malformed_root_does_not_throw(self):
        for p in (None, [], "bad", 1, {}, {"schema_version": 1}):
            with self.subTest(p=p):
                self.assertEqual(g.classify(p)["state"], "INVALID_PACKET")

    def test_cli_read_failure_is_json_and_no_private_path_echo(self):
        for error in (OSError("PRIVATE_SENTINEL"), UnicodeError("PRIVATE_SENTINEL"), ValueError("PRIVATE_SENTINEL")):
            with patch.object(g.Path, "read_text", side_effect=error), redirect_stdout(io.StringIO()) as out:
                self.assertEqual(g.main(["private.json"]), 1)
            self.assertEqual(json.loads(out.getvalue())["state"], "INVALID_PACKET")
            self.assertNotIn("PRIVATE_SENTINEL", out.getvalue())

    def test_cli_ready_and_invalid_shapes(self):
        for p, code in ((self.p, 0), ([], 1), ({}, 1)):
            with patch.object(g.Path, "read_text", return_value=json.dumps(p)), redirect_stdout(io.StringIO()) as out:
                self.assertEqual(g.main(["private.json"]), code)
            self.assertFalse(json.loads(out.getvalue())["recovery_verified"])


if __name__ == "__main__":
    unittest.main()
