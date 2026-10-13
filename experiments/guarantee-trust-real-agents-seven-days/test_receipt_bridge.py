"""Offline adversarial decoded fixtures; these are not live-chain receipts."""
import copy
import unittest
from receipt_bridge import ReceiptBridge

A='0x'+'1'*40
GT='0x'+'2'*40
TOKEN='0x036cbd53842c5426634e7929541ec2318f3dcf7e'
WORKER='0x'+'3'*40
HASH='0x'+'a'*64
TERMS='0x'+'b'*64


def fixture(action):
    expected={'action':action,'sender':A,'contract':GT,'token':TOKEN,'worker':WORKER,'amount':'100000',
              'termsHash':TERMS,'guaranteeAmount':'100000','guaranteeId':'7','grossWage':'200000'}
    name={'fund-reserve':'ReserveFunded','open':'GuaranteeOpened','pay':'Transfer','mark-paid':'GuaranteePaid','claim':'Claimed','cancel':'GuaranteeCancelled'}[action]
    method={'fund-reserve':'fundReserve','open':'openGuarantee','pay':'transfer','mark-paid':'markPaid','claim':'claim','cancel':'cancelGuarantee'}[action]
    args={'from':A,'amount':'100000','worker':WORKER,'termsHash':TERMS,'id':'7','to':WORKER,'value':'100000','wage':'200000'}
    target=TOKEN if action=='pay' else GT
    transfer={'address':TOKEN,'name':'Transfer','args':{'from':A,'to':GT,'value':'100000'}}
    if action=='pay':transfer['args']['to']=WORKER
    if action=='claim':transfer['args'].update({'from':GT,'to':WORKER})
    decoded={'schema':'verified-real-agents-action/1','registrationHash':'reg-hash','transactionHash':HASH,
             'chainId':84532,'status':1,'from':A,'to':target,'value':'0','action':action,'method':method,
             'blockNumber':123,'blockHash':'0x'+'c'*64,'event':{'address':target,'name':name,'args':args},
             'tokenTransfers':[transfer], 'guaranteeId':'7',
             'guarantee':{'worker':WORKER,'amount':'100000','termsHash':TERMS,'state':{'open':'1','mark-paid':'2','claim':'3','cancel':'4'}.get(action,'1')},
             'state':{'reserve':'400000','totalStake':'100000','contractTokenBalance':'500000','sponsorCapital':'350000','totalDues':'50000'}}
    return {'hash':'reg-hash','expected':expected},decoded


class TypedReceiptTests(unittest.TestCase):
    def test_legitimate_funding_open_payment_claim_cancel(self):
        for action in ('fund-reserve','open','pay','mark-paid','claim','cancel'):
            with self.subTest(action=action):
                reg,dec=fixture(action);ReceiptBridge._check_decoded(reg,dec,HASH)

    def assert_rejected(self, action, change):
        reg,decoded=fixture(action);change(decoded)
        with self.assertRaises(ValueError):ReceiptBridge._check_decoded(reg,decoded,HASH)

    def test_wrong_chain(self):self.assert_rejected('pay',lambda d:d.update(chainId=1))
    def test_wrong_sender(self):self.assert_rejected('fund-reserve',lambda d:d.update({'from':WORKER}))
    def test_wrong_worker(self):self.assert_rejected('open',lambda d:d['event']['args'].update(worker=A))
    def test_wrong_amount(self):self.assert_rejected('pay',lambda d:d['event']['args'].update(value='1'))
    def test_wrong_gt(self):self.assert_rejected('open',lambda d:d.update(to=A))
    def test_wrong_token(self):self.assert_rejected('pay',lambda d:d['tokenTransfers'][0].update(address=GT))
    def test_unrelated_mark_paid(self):self.assert_rejected('mark-paid',lambda d:d['event']['args'].update(id='8'))
    def test_original_arbitrary_probes(self):
        reg,d=fixture('fund-reserve')
        d={'verified':True,'semantic_evidence':{'kind':'funding'},'readbacks':[{'expected':'0x01'}]}
        with self.assertRaises((ValueError,KeyError)):ReceiptBridge._check_decoded(reg,d,HASH)
    def test_wrong_event_method(self):self.assert_rejected('pay',lambda d:d.update(method='approve'))
    def test_bad_worker_readback(self):self.assert_rejected('open',lambda d:d['guarantee'].update(worker=A))
    def test_wrong_terminal_state(self):self.assert_rejected('mark-paid',lambda d:d['guarantee'].update(state='1'))
    def test_books_mismatch(self):self.assert_rejected('claim',lambda d:d['state'].update(totalStake='0'))
    def test_wrong_registration_hash(self):self.assert_rejected('open',lambda d:d.update(registrationHash='other'))
    def test_wrong_receipt_hash(self):self.assert_rejected('open',lambda d:d.update(transactionHash='0x'+'d'*64))
    def test_token_transfer_wrong_source(self):self.assert_rejected('pay',lambda d:d['tokenTransfers'][0]['args'].update({'from':GT}))
    def test_token_transfer_wrong_recipient(self):self.assert_rejected('claim',lambda d:d['tokenTransfers'][0]['args'].update(to=A))
    def test_extra_duplicate_transfer(self):self.assert_rejected('pay',lambda d:d['tokenTransfers'].append(copy.deepcopy(d['tokenTransfers'][0])))

if __name__=='__main__':unittest.main()

class RegistrationTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        import json
        import hashlib
        from pathlib import Path
        from market import Market,COUNTS
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)
        personas={'actors':[{'id':f'{r}-{i+1:02d}','role':r,'public':{'name':f'{r}{i}'},
                    'private':{'notice':'offline test persona'}} for r,n in COUNTS.items() for i in range(n)]}
        p=self.root/'p.json';p.write_text(json.dumps(personas))
        self.market=Market.init(self.root/'run',p,GT)
        self.bridge=ReceiptBridge(self.market)
        artifact=self.root/'artifact.json';artifact.write_text('{"abi":[],"sourceCommit":"ec93c76779b5e2d52ab7b87cf82b3fd400205969"}')
        pin={'runId':'real-agents-offline-fixture','chainId':84532,'token':TOKEN,'contract':GT,'issuer':'0x38e9845A1Df22c59Bfc693bf2CEAa3361158d6d1','adjudicator':'0x38e9845A1Df22c59Bfc693bf2CEAa3361158d6d1',
             'artifactPath':str(artifact),'artifactSha256':hashlib.sha256(artifact.read_bytes()).hexdigest(),
             'runtimeSha256':'a'*64,'sourceCommit':'ec93c76779b5e2d52ab7b87cf82b3fd400205969','deploymentTransactionHash':HASH,
             'bootstrapEvidenceHash':'b'*64,'actors':{p['id']:{'role':p['role'],'address':A} for p in personas['actors']}}
        pin['actors']['issuer-01']['address']=pin['issuer'];pin['actors']['adjudicator-01']['address']=pin['adjudicator']
        self.bridge.pin(pin)
        self.market.state['verified_wallet_bootstrap']={'notice':'offline fixture only; not actual verified chain evidence'}
        result=self.market.command('sponsor-01',{'id':'fund','action':'propose_funding','amount_micro':100000})
        self.intent=result['intent_id']

    def tearDown(self):self.temp.cleanup()

    def action(self, amount='100000'):
        import json
        from receipt_bridge import ordered_hash
        norm={'runId':'real-agents-offline-fixture','intentId':self.intent,'day':1,'actorId':'sponsor-01',
              'action':'fund-reserve','args':[amount]}
        record={'actorId':'sponsor-01','day':1,'coordinatorApproved':True,'actionPayload':norm,'transcript':{'actorId':'sponsor-01','day':1,
                'acceptedActionPayload':norm,'prompt':'Explicit exact-action consent; offline fixture.',
                'response':json.dumps({'acceptedActionPayload':norm})}}
        rh=ordered_hash(record)
        action={**norm,'consent':{'actorId':'sponsor-01','payloadHash':ordered_hash(norm),'recordHash':rh},'evidence':{}}
        return action,[{'recordHash':rh,'record':record}]

    def test_funding_registration_derives_actual_model_amount(self):
        action,records=self.action();key=self.bridge.register(self.intent,action,records)
        self.assertEqual(self.market.state['receipt_registrations'][key]['expected']['amount'],'100000')
        self.assertEqual(self.market.state['confirmed']['sponsor_funding_micro'],0)

    def test_rehashed_wrong_amount_still_rejected(self):
        action,records=self.action('300000')
        with self.assertRaisesRegex(ValueError,'amount mismatch'):self.bridge.register(self.intent,action,records)

    def test_metadata_only_fake_consent_rejected(self):
        from receipt_bridge import ordered_hash
        action,records=self.action();record=records[0]['record'];record['transcript']['response']='{"agreed":true}'
        rh=ordered_hash(record);records[0]['recordHash']=rh;action['consent']['recordHash']=rh
        with self.assertRaisesRegex(ValueError,'explicitly accepted'):self.bridge.register(self.intent,action,records)

    def test_receipt_cannot_be_imported_without_pre_registration(self):
        with self.assertRaisesRegex(ValueError,'Registered typed action'):
            self.bridge.import_transaction(self.intent+':fund-reserve',HASH)

    def test_pin_cannot_be_replaced(self):
        with self.assertRaisesRegex(ValueError,'immutable'):self.bridge.pin(self.market.state['verification_pin'])
