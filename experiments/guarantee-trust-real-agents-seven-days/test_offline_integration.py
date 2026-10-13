"""Synthetic integration regressions; no cryptography, RPC, model or EVM use."""
import copy
import socket
import subprocess
import tempfile
import unittest

from receipt_bridge import ReceiptBridge, ordered_hash
from offline_integration import Scenario, MODE, ForbiddenOperation, consent, offline_guard, run


class OfflineIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.guard = offline_guard()
        self.guard.__enter__()
        self.scenario = Scenario(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()
        self.guard.__exit__(None, None, None)

    def unchanged_rejection(self, callback, message):
        s = self.scenario.market
        before = copy.deepcopy(s.state)
        files = {p.name: p.read_bytes() for p in s.root.iterdir() if p.is_file()}
        with self.assertRaisesRegex((ValueError, ForbiddenOperation), message):
            callback()
        self.assertEqual(s.state, before)
        self.assertEqual({p.name: p.read_bytes() for p in s.root.iterdir() if p.is_file()}, files)

    def test_lifecycle_seven_day_barriers_and_determinism(self):
        first = self.scenario.complete()
        second = run()
        self.assertEqual(first, second)
        self.assertEqual(first['syntheticAccounting'], {'sponsor_funding_micro': 400000,
                         'net_cash_received_micro': 190000, 'worker_wages_micro': 200000})
        self.assertEqual(first['importedStubReceipts'], 4)
        self.assertEqual(self.scenario.market.state['status'], 'days_complete')
        self.assertEqual(len(self.scenario.market.state['turn_receipts']), 700)
        self.assertFalse(first['custodySettlementVerified'])
        self.assertFalse(first['readyForLiveExecution'])
        for row in self.scenario.market.state['chain_receipts'].values():
            self.assertEqual(row['verified']['evidence_mode'], MODE)
        for record in self.scenario.records:
            self.assertEqual(record['record']['evidence_mode'], MODE)

    def test_initial_budget_is_400000_not_legacy_500000(self):
        self.unchanged_rejection(lambda: self.scenario.command('sponsor-01', 'propose_funding',
                                 amount_micro=500000), 'Initial reserve')

    def test_altered_consent_even_rehashed_is_rejected(self):
        s = self.scenario
        intent = s.command('sponsor-01', 'propose_funding', amount_micro=400000)
        action, records = s.action(intent, 'fund-reserve', 'sponsor-01', ['400000'])
        records[0]['record']['transcript']['response'] = '{"agreed":true}'
        rh = ordered_hash(records[0]['record'])
        records[0]['recordHash'] = rh
        action['consent']['recordHash'] = rh
        self.unchanged_rejection(lambda: s.register(action, records), 'explicitly accepted')

    def test_changed_nonce_after_consent_is_rejected(self):
        s = self.scenario
        s.import_receipt(*s.funding())
        action, records = s.opening()
        action['args'][0]['nonce'] = '1'
        self.unchanged_rejection(lambda: s.register(action, records), 'payload hash')

    def test_rehashed_wrong_terms_or_client_is_rejected(self):
        s = self.scenario
        s.import_receipt(*s.funding())
        action, records = s.opening()
        original = records[0]['record']['actionPayload']
        for field, message in [('termsHash', 'terms hash'), ('clientId', 'Client ID hash')]:
            normalized = copy.deepcopy(original)
            normalized['args'][0][field] = '0x' + 'f' * 64
            altered = consent(normalized, ['worker-01', 'client-01', 'issuer-01'])
            self.unchanged_rejection(lambda: s.register(*altered), message)

    def test_replay_receipt_rejected_without_accounting_or_file_change(self):
        s = self.scenario
        key, tx = s.funding()
        s.import_receipt(key, tx)
        self.unchanged_rejection(lambda: s.import_receipt(key, tx), 'already consumed')

    def test_same_transaction_cannot_confirm_other_registration(self):
        s = self.scenario
        key, tx = s.funding()
        s.import_receipt(key, tx)
        other = s.register(*s.opening())
        self.unchanged_rejection(lambda: s.import_receipt(other, tx), 'already consumed')

    def test_ambiguous_transfer_rejected_then_valid_retry(self):
        s = self.scenario
        key, tx = s.funding()
        row = s.provider.records[tx]['decoded']
        row['tokenTransfers'].append(copy.deepcopy(row['tokenTransfers'][0]))
        self.unchanged_rejection(lambda: s.import_receipt(key, tx), 'Exact Circle')
        row['tokenTransfers'].pop()
        s.import_receipt(key, tx)
        self.assertEqual(s.market.state['confirmed']['sponsor_funding_micro'], 400000)

    def test_unknown_fixture_and_provider_methods_fail_closed(self):
        s = self.scenario
        key, _ = s.funding()
        self.unchanged_rejection(lambda: s.import_receipt(key, '0x' + 'e' * 64), 'no fixture')
        self.unchanged_rejection(lambda: s.provider.request('eth_sendRawTransaction', ''), 'method denied')

    def test_no_default_live_verifier_for_synthetic_state(self):
        s = self.scenario
        key, tx = s.funding()
        self.unchanged_rejection(lambda: s.market.import_receipt(
            {'registration_key': key, 'transaction_hash': tx}), 'requires injected verifier')

    def test_injection_refused_for_live_state(self):
        s = self.scenario
        s.market.state.pop('evidence_mode')
        self.unchanged_rejection(lambda: ReceiptBridge(s.market, verifier=s.verifier), 'requires synthetic')

    def test_sign_broadcast_publication_and_network_stubs_deny(self):
        for transport in (self.scenario.sign, self.scenario.broadcast,
                          self.scenario.publish, self.scenario.network):
            self.unchanged_rejection(transport, 'transport denied')
            self.assertEqual(transport.attempts, 1)

    def test_network_and_subprocess_attempts_cannot_escape_transport(self):
        self.unchanged_rejection(lambda: socket.socket(), 'process denied: socket')
        self.unchanged_rejection(lambda: subprocess.run(['git', '--version']), 'process denied: subprocess')

    def test_injected_verifier_cannot_fall_back_to_network(self):
        s = self.scenario
        key, tx = s.funding()
        def malicious_verifier(request):
            return socket.create_connection(('127.0.0.1', 1))
        self.unchanged_rejection(lambda: s.market.import_receipt(
            {'registration_key': key, 'transaction_hash': tx}, verifier=malicious_verifier), 'process denied')

    def test_stale_pin_rejected_before_verifier(self):
        s = self.scenario
        key, tx = s.funding()
        s.market.state['verification_pin']['runtimeSha256'] = 'e' * 64
        self.unchanged_rejection(lambda: s.import_receipt(key, tx), 'pin changed')

    def test_unlabeled_stub_result_rejected(self):
        s = self.scenario
        key, tx = s.funding()
        s.provider.records[tx]['decoded'].pop('evidence_mode')
        self.unchanged_rejection(lambda: s.import_receipt(key, tx), 'label synthetic')

    def test_wrong_decoded_identity_rejected(self):
        s = self.scenario
        key, tx = s.funding()
        s.provider.records[tx]['decoded']['chainId'] = 1
        self.unchanged_rejection(lambda: s.import_receipt(key, tx), 'Chain/transaction')


if __name__ == '__main__':
    unittest.main()
