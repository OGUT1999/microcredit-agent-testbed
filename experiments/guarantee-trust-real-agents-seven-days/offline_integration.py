#!/usr/bin/env python3
"""Deterministic synthetic integration, stdlib only; never a chain/model receipt."""
import copy
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

from market import Market, COUNTS, TOKEN, digest, encode, require, save
from receipt_bridge import ReceiptBridge, ordered_hash

MODE = 'synthetic-offline/1'
NOTICE = 'SYNTHETIC OFFLINE FIXTURE: no model, signature, EVM, payment or human benefit.'
HERE = Path(__file__).resolve().parent
GT = '0x' + '2' * 40
ROOT_ADDRESS = '0x38e9845a1df22c59bfc693bf2ceaa3361158d6d1'  # public schema value only
BLOCK = '0x' + 'c' * 64
RUN = 'synthetic-offline-integration-v1'


class ForbiddenOperation(RuntimeError):
    pass


class DeniedTransport:
    def __init__(self, name):
        self.name = name
        self.attempts = 0

    def __call__(self, *args, **kwargs):
        self.attempts += 1
        raise ForbiddenOperation('Offline transport denied: ' + self.name)


@contextmanager
def offline_guard():
    """Process-local defense in depth. No OS/network/security settings changed."""
    active = [True]

    def audit(event, args):
        if active[0] and (event.startswith('socket.') or event.startswith('os.exec')
                          or event.startswith('os.spawn')
                          or event in ('subprocess.Popen', 'os.system', 'os.posix_spawn', 'pty.spawn')):
            raise ForbiddenOperation('Offline process denied: ' + event)

    sys.addaudithook(audit)
    try:
        yield
    finally:
        active[0] = False


class FixtureProvider:
    """Finite in-memory records; unknown methods/transactions never fall back to RPC."""
    def __init__(self):
        self.records = {}

    def request(self, method, key):
        require(method == 'synthetic_receipt', 'Offline provider method denied')
        require(key in self.records, 'Offline provider has no fixture')
        return copy.deepcopy(self.records[key])


class FixtureVerifier:
    """Transport stub, NOT the JavaScript verifier or independent chain validation."""
    def __init__(self, provider):
        self.provider = provider

    def __call__(self, request):
        if request.get('operation') == 'bootstrap':
            require(request['fundingTransactions'] == [], 'Synthetic bootstrap takes no transactions')
            return {'schema': 'verified-real-agents-bootstrap/1', 'chainId': 84532,
                    'runId': RUN, 'totalMicro': '38200000', 'evidence_mode': MODE, 'notice': NOTICE}
        record = self.provider.request('synthetic_receipt', request['transactionHash'])
        require(record['pin_hash'] == digest(request['pin']), 'Synthetic pin mismatch')
        require(record['registration_hash'] == request['registrationHash'], 'Synthetic registration mismatch')
        return record['decoded']


def consent(normalized, actors):
    records = []
    for actor in actors:
        record = {'evidence_mode': MODE, 'notice': NOTICE, 'actorId': actor,
                  'day': normalized['day'], 'coordinatorApproved': True,
                  'actionPayload': copy.deepcopy(normalized),
                  'transcript': {'actorId': actor, 'day': normalized['day'],
                                 'prompt': NOTICE + '\nAccept exact fixture: ' + encode(normalized),
                                 'acceptedActionPayload': copy.deepcopy(normalized),
                                 'response': encode({'notice': NOTICE, 'acceptedActionPayload': normalized})}}
        records.append({'recordHash': ordered_hash(record), 'record': record})
    action = {**copy.deepcopy(normalized), 'consent': {
        'actorId': normalized['actorId'], 'payloadHash': ordered_hash(normalized),
        'recordHash': records[0]['recordHash']}, 'evidence': {}}
    if normalized['action'] == 'open':
        action['evidence'] = dict(zip(('clientConsentHash', 'issuerConsentHash'),
                                     [r['recordHash'] for r in records[1:]]))
    return action, records


class Scenario:
    def __init__(self, directory):
        directory = Path(directory)
        personas = {'actors': [{'id': f'{role}-{i+1:02d}', 'role': role,
                               'public': {'name': 'Synthetic ' + role}, 'private': {'notice': NOTICE}}
                              for role, count in COUNTS.items() for i in range(count)]}
        source = directory / 'synthetic-personas.json'
        save(source, personas)
        self.market = Market.init(directory / 'synthetic-run', source, GT)
        self.market.state['evidence_mode'] = MODE
        self.provider = FixtureProvider()
        self.verifier = FixtureVerifier(self.provider)
        self.sign = DeniedTransport('signing')
        self.broadcast = DeniedTransport('broadcast')
        self.publish = DeniedTransport('publication')
        self.network = DeniedTransport('network/model')
        self.bridge = ReceiptBridge(self.market, verifier=self.verifier)
        artifact = HERE.parent / 'guarantee-trust-circle-coldstart/artifact.json'
        actors = {p['id']: {'role': p['role'], 'address': '0x' + f'{i+100:040x}'}
                  for i, p in enumerate(personas['actors'])}
        for actor in ('issuer-01', 'adjudicator-01'):
            actors[actor]['address'] = ROOT_ADDRESS
        self.pin = {'runId': RUN, 'chainId': 84532, 'token': TOKEN, 'contract': GT,
                    'issuer': ROOT_ADDRESS, 'adjudicator': ROOT_ADDRESS,
                    'artifactPath': str(artifact), 'artifactSha256': hashlib.sha256(artifact.read_bytes()).hexdigest(),
                    'runtimeSha256': 'a' * 64, 'sourceCommit': 'ec93c76779b5e2d52ab7b87cf82b3fd400205969',
                    'deploymentTransactionHash': '0x' + 'd' * 64, 'bootstrapEvidenceHash': 'b' * 64,
                    'actors': actors, 'evidence_mode': MODE, 'notice': NOTICE}
        self.bridge.pin(self.pin)
        self.bridge.verify_bootstrap([])
        self.records = []
        self.imported = []

    def command(self, actor, action, **kwargs):
        cmd = {'id': action, 'action': action, **kwargs}
        result = self.market.command(actor, cmd)
        self.market.event('synthetic_command', {'notice': NOTICE, 'actor': actor, 'command': cmd, 'result': result})
        return result.get('intent_id')

    def action(self, intent, kind, actor, args, parties=None):
        norm = {'runId': RUN, 'intentId': intent, 'day': 1, 'actorId': actor,
                'action': kind, 'args': args}
        return consent(norm, parties or [actor])

    def register(self, action, records):
        key = self.bridge.register(action['intentId'], action, records)
        self.records.extend(copy.deepcopy(records))
        return key

    def fixture(self, key):
        """Known synthetic ledger expectations, kept separate from verifier request."""
        reg = self.market.state['receipt_registrations'][key]
        kind = reg['expected']['action']
        tx = '0x' + hashlib.sha256(('SYNTHETIC:' + kind).encode()).hexdigest()
        wallet = lambda actor: self.pin['actors'][actor]['address']
        job = self.market.state['jobs'].get('synthetic-job', {})
        terms = '0x' + job.get('hire_terms_hash', '0' * 64)
        sender = {'fund-reserve': wallet('sponsor-01'), 'open': ROOT_ADDRESS,
                  'pay': wallet('client-01'), 'mark-paid': ROOT_ADDRESS}[kind]
        method, event = {'fund-reserve': ('fundReserve', 'ReserveFunded'),
                         'open': ('openGuarantee', 'GuaranteeOpened'),
                         'pay': ('transfer', 'Transfer'), 'mark-paid': ('markPaid', 'GuaranteePaid')}[kind]
        amount = {'fund-reserve': '400000', 'open': '80000', 'pay': '190000', 'mark-paid': '200000'}[kind]
        args = {'from': sender, 'worker': wallet('worker-01'), 'to': wallet('worker-01'),
                'amount': amount, 'value': amount, 'termsHash': terms, 'id': '1', 'wage': '200000'}
        target = TOKEN if kind == 'pay' else GT
        transfers = []
        if kind in ('fund-reserve', 'pay'):
            transfers = [{'address': TOKEN, 'name': 'Transfer', 'args': {
                'from': sender, 'to': GT if kind == 'fund-reserve' else wallet('worker-01'), 'value': amount}}]
        decoded = {'evidence_mode': MODE, 'notice': NOTICE, 'schema': 'verified-real-agents-action/1',
                   'registrationHash': reg['hash'], 'transactionHash': tx, 'chainId': 84532,
                   'status': 1, 'from': sender, 'to': target, 'value': '0', 'action': kind, 'method': method,
                   'blockNumber': 123, 'blockHash': BLOCK, 'event': {'address': target, 'name': event, 'args': args},
                   'tokenTransfers': transfers, 'guaranteeId': '1',
                   'guarantee': {'worker': wallet('worker-01'), 'amount': '80000', 'termsHash': terms,
                                 'state': '2' if kind == 'mark-paid' else '1'},
                   'state': {'reserve': '400000', 'totalStake': '0', 'contractTokenBalance': '400000',
                             'sponsorCapital': '400000', 'totalDues': '0'}}
        self.provider.records[tx] = {'pin_hash': digest(self.pin), 'registration_hash': reg['hash'], 'decoded': decoded}
        return tx

    def import_receipt(self, key, tx):
        self.market.import_receipt({'registration_key': key, 'transaction_hash': tx}, verifier=self.verifier)
        self.imported.append(tx)

    def funding(self):
        intent = self.command('sponsor-01', 'propose_funding', amount_micro=400000, text=NOTICE)
        key = self.register(*self.action(intent, 'fund-reserve', 'sponsor-01', ['400000']))
        tx = self.fixture(key)
        return key, tx

    def opening(self):
        self.command('client-01', 'post_job', job_id='synthetic-job', amount_micro=200000,
                     title='Synthetic three-line fixture', description=NOTICE)
        self.command('worker-01', 'apply', job_id='synthetic-job', text=NOTICE)
        self.command('client-01', 'hire', job_id='synthetic-job', worker_id='worker-01', text=NOTICE)
        self.command('worker-01', 'accept_terms', job_id='synthetic-job', text=NOTICE)
        intent = self.command('issuer-01', 'propose_guarantee', job_id='synthetic-job',
                              worker_id='worker-01', amount_micro=80000, text=NOTICE)
        job = self.market.state['jobs']['synthetic-job']
        acceptance = {'worker': self.pin['actors']['worker-01']['address'], 'amount': '80000',
                      'clientId': '0x' + hashlib.sha256(job['client'].encode()).hexdigest(),
                      'termsHash': '0x' + job['hire_terms_hash'], 'contributionBps': '500',
                      'contributionCap': '3000000', 'nonce': '0', 'deadline': '1800000000'}
        return self.action(intent, 'open', 'worker-01', [acceptance], ['worker-01', 'client-01', 'issuer-01'])

    def complete(self):
        self.import_receipt(*self.funding())
        key = self.register(*self.opening())
        self.import_receipt(key, self.fixture(key))
        self.command('worker-01', 'deliver', job_id='synthetic-job', text=NOTICE + '\nOne\nTwo\nThree')
        self.command('client-01', 'review', job_id='synthetic-job', accepted=True, text=NOTICE)
        intent = self.command('client-01', 'propose_payment', job_id='synthetic-job')
        key = self.register(*self.action(intent, 'pay', 'client-01', ['worker-01', '190000']))
        self.import_receipt(key, self.fixture(key))
        action, records = self.action(intent, 'mark-paid', 'adjudicator-01', ['1', '200000', 'synthetic evidence'])
        action['evidence']['verifiedPaymentHash'] = self.market.state['jobs']['synthetic-job']['verified_payment_hash']
        key = self.register(action, records)
        self.import_receipt(key, self.fixture(key))
        # The real submit/advance path receives 700 plainly labeled static packets.
        # These are canned passes, not fresh model contexts or economic decisions.
        for _ in range(7):
            for actor in self.market.state['queue']:
                packet = {'actor_id': actor, 'day': self.market.state['day'], 'prompt': self.market.brief(actor),
                          'response': encode({'dialogue': NOTICE, 'journal': NOTICE, 'commands': []}),
                          'model_context': NOTICE}
                self.market.submit(packet)
            self.market.advance()
        return {'schema': MODE, 'notice': NOTICE, 'fixtureDays': 7, 'cannedPassPackets': 700,
                'importedStubReceipts': len(self.imported), 'syntheticAccounting': self.market.state['confirmed'],
                'jobStatus': self.market.state['jobs']['synthetic-job']['status'],
                'termsHash': self.market.state['jobs']['synthetic-job']['hire_terms_hash'],
                'consentRecordsSha256': digest(self.records),
                'actualModelCalls': 0, 'actualSignatures': 0, 'actualEVMTransactions': 0,
                'publicationCalls': self.publish.attempts, 'readyForLiveExecution': False,
                'custodySettlementVerified': False, 'humanBenefitVerified': False}


def run():
    with offline_guard(), tempfile.TemporaryDirectory(prefix='synthetic-seven-day-') as directory:
        return Scenario(directory).complete()


if __name__ == '__main__':
    # No children are used. Remove publishing/wallet/provider credentials before work.
    os.environ.clear()
    print(json.dumps(run(), indent=2, sort_keys=True))
