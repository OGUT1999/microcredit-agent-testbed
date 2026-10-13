"""Typed action registration and independently checked, live decoded receipts.

The only production verifier entry point starts the pinned local Node helper.
No method accepts caller-supplied decoded receipt assertions as trusted evidence.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from market import require, digest, encode, save, TOKEN


def ordered_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def addr(value):
    require(isinstance(value, str) and re.fullmatch(r'0x[0-9a-fA-F]{40}', value), 'Invalid address')
    return value.lower()


def integer(value):
    require(isinstance(value, str) and re.fullmatch(r'\d{1,20}', value), 'Canonical amount string required')
    return int(value)


class ReceiptBridge:
    def __init__(self, market):
        self.market = market

    def pin(self, pin):
        """Coordinator installs independently reviewed deployment+ABI/bootstrap evidence once."""
        require(not self.market.state.get('verification_pin'), 'Deployment pin immutable')
        require(pin['chainId'] == 84532 and addr(pin['token']) == TOKEN, 'Wrong chain/token pin')
        require(addr(pin['contract']) == addr(self.market.state['chain']['contract']), 'Contract pin mismatch')
        require(re.fullmatch(r'[a-f0-9]{64}', pin['runtimeSha256']), 'Runtime hash required')
        artifact_bytes=Path(pin['artifactPath']).read_bytes()
        artifact=json.loads(artifact_bytes)
        require(pin['sourceCommit']=='ec93c76779b5e2d52ab7b87cf82b3fd400205969'
                and artifact.get('sourceCommit')==pin['sourceCommit'], 'Pinned artifact source revision mismatch')
        actual = hashlib.sha256(artifact_bytes).hexdigest()
        require(actual == pin['artifactSha256'], 'ABI artifact hash mismatch')
        require(re.fullmatch(r'0x[0-9a-fA-F]{64}', pin['deploymentTransactionHash']), 'Deployment receipt hash required')
        require(re.fullmatch(r'[a-f0-9]{64}',pin.get('bootstrapEvidenceHash','')), 'Pinned bootstrap evidence hash required')
        root='0x38e9845a1df22c59bfc693bf2ceaa3361158d6d1'
        require(addr(pin['issuer'])==root and addr(pin['adjudicator'])==root, 'Issuer/adjudicator must bind authorized root')
        require(set(pin['actors']) == set(self.market.personas), 'Wallet identities must cover exact roster')
        for actor, wallet in pin['actors'].items():
            require(wallet['role'] == self.market.personas[actor]['role'], 'Wallet role mismatch')
            addr(wallet['address'])
        require(addr(pin['actors']['issuer-01']['address']) == addr(pin['issuer']), 'Issuer address mismatch')
        require(addr(pin['actors']['adjudicator-01']['address']) == addr(pin['adjudicator']), 'Adjudicator address mismatch')
        self.market.state['verification_pin'] = pin
        self.market.event('verification_pin', {'pin': pin})
        save(self.market.state_path, self.market.state)

    def verify_bootstrap(self, funding_transactions):
        """Independent actual receipt coverage for all client/backer/sponsor distributions."""
        s=self.market.state;pin=s.get('verification_pin')
        require(pin is not None, 'Deployment pin required')
        require(not s.get('verified_wallet_bootstrap'), 'Bootstrap receipt registry immutable')
        request={'operation':'bootstrap','pin':pin,'fundingTransactions':funding_transactions}
        node=os.environ.get('CODEX_PRIMARY_RUNTIME_NODE','node')
        helper=Path(__file__).with_name('receipt_verifier.mjs')
        completed=subprocess.run([node,str(helper)],input=encode(request),text=True,capture_output=True,check=False,timeout=90)
        require(completed.returncode==0,'Independent bootstrap receipt verification failed')
        decoded=json.loads(completed.stdout)
        require(decoded.get('schema')=='verified-real-agents-bootstrap/1' and decoded.get('chainId')==84532
                and decoded.get('runId')==pin['runId'] and decoded.get('totalMicro')=='38200000',
                'Bootstrap result mismatch')
        s['verified_wallet_bootstrap']=decoded
        self.market.event('independently_verified_wallet_bootstrap',decoded)
        save(self.market.state_path,s)

    def register(self, intent_id, action, consent_records):
        """Register before broadcast. Core parties/values derive from engine intent and job."""
        s = self.market.state
        require('verification_pin' in s, 'Reviewed deployment pin missing')
        require(s.get('verified_wallet_bootstrap'), 'Independently verified role-wallet bootstrap required before actions')
        intent = s['intents'][intent_id]
        require(intent['status'] == 'pending', 'Intent not pending')
        pin = s['verification_pin']
        require(action['runId'] == pin['runId'] and action['day'] == intent['day'], 'Run/day mismatch')
        require(action['intentId'] == intent_id, 'Action intent must bind model intention')
        kind = action['action']; args = action['args']; actor = action['actorId']
        require(actor in self.market.personas, 'Unknown actor')
        normalized = {k:action[k] for k in ('runId','intentId','day','actorId','action','args')}
        require(action['consent']['actorId'] == actor and action['consent']['payloadHash'] == ordered_hash(normalized), 'Action consent payload hash mismatch')
        consent_hash = action['consent']['recordHash']
        records = {r['recordHash']:r['record'] for r in consent_records}
        record = records.get(consent_hash)
        require(record and ordered_hash(record) == consent_hash, 'Missing exact hashed consent record')
        # Explicit accepted typed action is mandatory; no application/journal inference.
        require(record.get('coordinatorApproved') is True, 'Coordinator-reviewed exact consent required')
        require(record.get('actorId') == actor and record.get('day') == intent['day'] and record.get('actionPayload') == normalized,
                'Exact actor/day/action consent required')
        transcript = record.get('transcript', {})
        require(transcript.get('actorId') == actor and transcript.get('day') == intent['day'] and transcript.get('acceptedActionPayload') == normalized,
                'Accepted typed action transcript absent')
        require(isinstance(transcript.get('prompt'),str) and isinstance(transcript.get('response'),str),
                'Exact typed-action consent prompt and response required')
        accepted_response=json.loads(transcript['response'])
        require(isinstance(accepted_response,dict) and accepted_response.get('acceptedActionPayload')==normalized,
                'Exact typed action must be explicitly accepted in unmodified model JSON response')
        expected = {'action':kind,'sender':pin['actors'][actor]['address'],
                    'contract':pin['contract'],'token':pin['token']}
        payload = intent['payload']; job = s['jobs'].get(payload.get('job_id'))
        def role(r): require(self.market.personas[actor]['role'] == r, 'Wrong action role')
        if kind == 'fund-reserve':
            role('sponsor'); require(intent['kind']=='funding' and actor==intent['actor'], 'Funding intention mismatch')
            require(len(args)==1 and integer(args[0])==payload['amount_micro'], 'Funding amount mismatch')
            expected.update(amount=args[0],args=args)
        elif kind == 'attest':
            role('backer'); require(intent['kind']=='backing' and actor==intent['actor'], 'Backing intention mismatch')
            require(len(args)==2 and args[0]==payload['worker_id'] and integer(args[1])==payload['amount_micro'], 'Backing worker/amount mismatch')
            require(actor in s.get('backer_permissions',{}).get(args[0],{}), 'Worker backing permission absent')
            expected.update(worker=pin['actors'][args[0]]['address'], amount=args[1],args=[pin['actors'][args[0]]['address'],args[1]])
        elif kind == 'open':
            role('worker'); require(intent['kind']=='open_guarantee' and actor==payload['worker_id'], 'Opening worker mismatch')
            require(job and job.get('worker_acceptance',{}).get('hire_terms_hash')==job.get('hire_terms_hash'), 'Fresh exact worker terms acceptance required')
            require(len(args)==1 and isinstance(args[0],dict), 'Acceptance tuple required')
            acceptance=args[0]
            require(addr(acceptance['worker'])==addr(pin['actors'][actor]['address']), 'Acceptance wallet mismatch')
            require(integer(acceptance['amount'])==payload['amount_micro'], 'Guarantee amount mismatch')
            require(acceptance['termsHash'].lower()=='0x'+job['hire_terms_hash'], 'Acceptance terms hash mismatch')
            # Client and group hashes must bind the registered job's real model client.
            client_hash='0x'+hashlib.sha256(job['client'].encode()).hexdigest()
            require(acceptance['clientId'].lower()==client_hash, 'Client ID hash mismatch')
            for consent_actor, key in ((job['client'],'clientConsentHash'),('issuer-01','issuerConsentHash')):
                c = records.get(action.get('evidence',{}).get(key,''))
                require(c and ordered_hash(c)==action['evidence'][key] and c.get('actorId')==consent_actor
                        and c.get('actionPayload')==normalized and c.get('day')==intent['day']
                        and c.get('coordinatorApproved') is True, 'Exact client/issuer opening consent missing')
                t=c.get('transcript',{})
                require(t.get('actorId')==consent_actor and t.get('day')==intent['day']
                        and t.get('acceptedActionPayload')==normalized and isinstance(t.get('prompt'),str)
                        and isinstance(t.get('response'),str)
                        and json.loads(t['response']).get('acceptedActionPayload')==normalized,
                        'Client/issuer original explicit action acceptance missing')
            require(integer(acceptance['contributionBps'])<=500 and integer(acceptance['contributionCap'])==3000000,
                    'Contribution terms exceed limits')
            expected.update(sender=pin['issuer'],worker=acceptance['worker'],amount=acceptance['amount'],
                            guaranteeAmount=acceptance['amount'],termsHash=acceptance['termsHash'],acceptance=acceptance)
        elif kind in ('pay','mark-paid','claim','cancel'):
            require(job and job.get('guarantee_id') is not None, 'Verified exact opened guarantee required')
            guarantee_id=str(job['guarantee_id']); worker=pin['actors'][job['worker']]['address']
            expected.update(worker=worker,guaranteeId=guarantee_id,
                            guaranteeAmount=str(job['guarantee_amount_micro']),termsHash='0x'+job['hire_terms_hash'])
            if kind=='pay':
                role('client'); require(intent['kind']=='payment' and actor==job['client'], 'Paying client mismatch')
                require(job['deliveries'] and job['reviews'] and job['reviews'][-1]['accepted'], 'Actual delivery and client acceptance required')
                bps=int(job['acceptance']['contributionBps']); cap=int(job['acceptance']['contributionCap'])
                net=job['amount_micro']-min(job['amount_micro']*bps//10000,cap)
                require(len(args)==2 and args[0]==job['worker'] and integer(args[1])==net, 'Net wage/worker mismatch')
                expected.update(amount=str(net),grossWage=str(job['amount_micro']),args=[worker,str(net)])
            elif kind=='mark-paid':
                role('adjudicator'); require(intent['kind']=='payment' and job.get('verified_payment_hash'), 'Verified actual cash payment required')
                require(len(args)==3 and args[0]==guarantee_id and integer(args[1])==job['amount_micro'], 'Mark-paid gross wage or guarantee mismatch')
                require(action.get('evidence',{}).get('verifiedPaymentHash')==job['verified_payment_hash'], 'Payment evidence hash mismatch')
                expected.update(grossWage=args[1],args=args)
            elif kind=='claim':
                role('adjudicator'); require(intent['kind']=='claim', 'Claim intention mismatch')
                require(job['deliveries'] and job['disputes'] and job['decisions'][-1]['decision']=='approve_claim', 'Actual work/dispute/adjudication required')
                require(len(args)==2 and args[0]==guarantee_id, 'Claim guarantee mismatch')
                expected.update(amount=str(job['guarantee_amount_micro']),args=args)
            else:
                role('adjudicator'); require(intent['kind']=='cancel', 'Cancellation intention mismatch')
                require(len(args)==2 and args[0]==guarantee_id, 'Cancellation guarantee mismatch')
                expected.update(args=args)
        else:
            raise ValueError('Unsupported registration: '+kind)
        registration={'intent_id':intent_id,'typed_action':normalized,'expected':expected,
                      'consent_record_hash':consent_hash,'pin_hash':digest(pin)}
        registration_hash=digest(registration)
        key=intent_id+':'+kind
        existing=s.setdefault('receipt_registrations',{}).get(key)
        require(existing is None or existing['hash']==registration_hash, 'Registration immutable')
        s['receipt_registrations'][key]={'hash':registration_hash,**registration}
        self.market.event('typed_action_registered',{'key':key,'registration':registration})
        save(self.market.state_path,s)
        return key

    def import_transaction(self, key, transaction_hash):
        s=self.market.state
        require(key in s.get('receipt_registrations',{}), 'Registered typed action required; arbitrary proofs disabled')
        require(re.fullmatch(r'0x[0-9a-fA-F]{64}',transaction_hash), 'Transaction hash required')
        registration=s['receipt_registrations'][key]
        require(not registration.get('receipt_hash'), 'Registered action receipt already consumed')
        require(transaction_hash not in s['chain_receipts'], 'Receipt already consumed')
        pin=s['verification_pin']; require(registration['pin_hash']==digest(pin), 'Deployment pin changed')
        request={'pin':pin,'expected':registration['expected'],'registrationHash':registration['hash'],'transactionHash':transaction_hash}
        node=os.environ.get('CODEX_PRIMARY_RUNTIME_NODE','node')
        helper=Path(__file__).with_name('receipt_verifier.mjs')
        completed=subprocess.run([node,str(helper)],input=encode(request),text=True,capture_output=True,check=False,timeout=90)
        require(completed.returncode==0, 'Pinned live receipt verifier rejected transaction; no accounting updated')
        decoded=json.loads(completed.stdout)
        self._check_decoded(registration,decoded,transaction_hash)
        intent=s['intents'][registration['intent_id']]; action=registration['expected']['action']
        job=s['jobs'].get(intent['payload'].get('job_id'))
        if action=='pay':
            job['verified_payment_hash']=transaction_hash;job['status']='cash_received_pending_mark_paid'
            s['confirmed'].setdefault('net_cash_received_micro',0)
            s['confirmed']['net_cash_received_micro']+=int(registration['expected']['amount'])
        else:
            intent['status']='confirmed';intent['transaction_hash']=transaction_hash
            if action=='fund-reserve':
                s['confirmed']['sponsor_funding_micro']+=intent['payload']['amount_micro'];s['bootstrap_barrier']=False
            elif action=='open':
                job.update(status='open',guarantee_id=decoded['guaranteeId'],guarantee_amount_micro=int(registration['expected']['amount']),
                           acceptance=registration['expected']['acceptance'])
            elif action=='mark-paid':
                job['status']='paid';s['confirmed']['worker_wages_micro']+=job['amount_micro']
            elif action=='claim': job['status']='claimed'
            elif action=='cancel': job['status']='cancelled'
        registration['receipt_hash']=transaction_hash
        s['chain_receipts'][transaction_hash]={'registration_key':key,'verified':decoded}
        self.market.event('independently_verified_typed_receipt',{'registration_key':key,'decoded':decoded})
        save(self.market.state_path,s)

    @staticmethod
    def _check_decoded(registration, decoded, txhash):
        """Defence in depth; tests exercise this pure predicate with adversarial fixtures."""
        e=registration['expected']
        require(decoded['schema']=='verified-real-agents-action/1' and decoded['registrationHash']==registration['hash'], 'Registration result mismatch')
        require(decoded['chainId']==84532 and decoded['status']==1 and decoded['transactionHash']==txhash, 'Chain/transaction mismatch')
        require(addr(decoded['from'])==addr(e['sender']) and decoded['value']=='0', 'Wrong sender/value')
        require(decoded['action']==e['action'], 'Wrong operation')
        target=e['token'] if e['action']=='pay' else e['contract']
        require(addr(decoded['to'])==addr(target) and addr(decoded['event']['address'])==addr(target), 'Wrong target/event address')
        methods={'fund-reserve':'fundReserve','attest':'attest','open':'openGuarantee','pay':'transfer','mark-paid':'markPaid','claim':'claim','cancel':'cancelGuarantee'}
        names={'fund-reserve':'ReserveFunded','attest':'Attested','open':'GuaranteeOpened','pay':'Transfer','mark-paid':'GuaranteePaid','claim':'Claimed','cancel':'GuaranteeCancelled'}
        require(decoded['method']==methods[e['action']] and decoded['event']['name']==names[e['action']], 'Wrong function/event')
        require(isinstance(decoded['blockNumber'],int) and decoded['blockNumber']>0 and re.fullmatch(r'0x[0-9a-fA-F]{64}',decoded['blockHash']), 'Pinned block identity required')
        event=decoded['event']['args']
        if e['action'] in ('fund-reserve','attest'):
            require(int(event['amount'])==int(e['amount']), 'Wrong amount')
        if e['action']=='fund-reserve': require(addr(event['from'])==addr(e['sender']), 'Wrong funder')
        if e['action']=='attest': require(addr(event['attester'])==addr(e['sender']) and addr(event['member'])==addr(e['worker']), 'Wrong backing identities')
        if e['action']=='open':
            require(addr(event['worker'])==addr(e['worker']) and int(event['amount'])==int(e['amount'])
                    and event['termsHash']==e['termsHash'], 'Wrong opened worker/terms/amount')
        if e['action']=='pay':
            require(addr(event['from'])==addr(e['sender']) and addr(event['to'])==addr(e['worker'])
                    and int(event['value'])==int(e['amount']), 'Wrong paid worker/amount')
        if e['action']=='mark-paid':
            require(event['id']==e['guaranteeId'] and event['wage']==e['grossWage'], 'Wrong paid guarantee/wage')
        if e['action'] in ('open','mark-paid','claim','cancel'):
            g=decoded['guarantee']
            require(addr(g['worker'])==addr(e['worker']) and g['amount']==e['guaranteeAmount']
                    and g['termsHash']==e['termsHash'], 'Guarantee readback mismatch')

        if e['action'] in ('fund-reserve','pay','claim'):
            source=e['contract'] if e['action']=='claim' else e['sender']
            destination=e['contract'] if e['action']=='fund-reserve' else e['worker']
            matches=[t for t in decoded['tokenTransfers'] if addr(t['address'])==addr(e['token'])
                     and addr(t['args']['from'])==addr(source) and addr(t['args']['to'])==addr(destination)
                     and int(t['args']['value'])==int(e['amount'])]
            require(len(matches)==1, 'Exact Circle USDC transfer required')
        if e['action'] in ('open','mark-paid','claim','cancel'):
            require(decoded['guarantee']['state']=={'open':'1','mark-paid':'2','claim':'3','cancel':'4'}[e['action']], 'Wrong guarantee state')
        state=decoded['state']
        require(int(state['reserve'])+int(state['totalStake'])==int(state['contractTokenBalance'])
                and int(state['sponsorCapital'])+int(state['totalDues'])==int(state['reserve']), 'Chain books mismatch')
