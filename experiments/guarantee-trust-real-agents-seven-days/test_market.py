import json
from pathlib import Path
import tempfile
import unittest
from market import Market, COUNTS, TOKEN


class MarketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.characters = []
        for role, count in COUNTS.items():
            for n in range(count):
                self.characters.append({'id': f'{role}{n}', 'name': f'{role} {n}', 'role': role,
                                        'public_bio': 'Fictional public occupation.',
                                        'private_brief': f'PRIVATE-{role}-{n}'})
        p = self.root / 'source.json'; p.write_text(json.dumps({'characters': self.characters}))
        self.market = Market.init(self.root / 'run', p, '0x' + '1'*40)
        self.market.state['verified_wallet_bootstrap']={'notice':'offline test fixture only'}

    def tearDown(self):
        self.temp.cleanup()

    def packet(self, actor, commands, journal='Honest fictional journal.'):
        return {'actor_id': actor, 'day': self.market.state['day'], 'prompt': self.market.brief(actor),
                'response': json.dumps({'dialogue': '', 'journal': journal, 'commands': commands}),
                'model_context': 'unit-test fixture; not an actual model run'}

    def test_private_visibility(self):
        prompt = self.market.brief('client0')
        self.assertIn('PRIVATE-client-0', prompt)
        self.assertNotIn('PRIVATE-worker-0', prompt)
        self.market.state['messages'] = [{'from': 'worker0', 'to': 'client1', 'text': 'PRIVATE-MESSAGE'}]
        self.market.state['journals']['client1'] = [{'text': 'PRIVATE-JOURNAL'}]
        prompt = self.market.brief('client0')
        self.assertNotIn('PRIVATE-MESSAGE', prompt)
        self.assertNotIn('PRIVATE-JOURNAL', prompt)

    def test_unauthorized_command_rejected_in_exact_transcript(self):
        packet = self.packet('client0', [{'id': 'bad', 'action': 'propose_funding', 'amount_micro': 100000}])
        result = self.market.submit(packet)
        self.assertEqual(result['results'][0]['result']['status'], 'rejected')
        events = [json.loads(l) for l in (self.market.root/'events.jsonl').read_text().splitlines()]
        self.assertEqual(events[-1]['payload']['response'], packet['response'])
        self.assertEqual(self.market.state['confirmed']['sponsor_funding_micro'], 0)

    def test_append_only_and_idempotent_turn(self):
        packet = self.packet('client0', [{'id': 'say', 'action': 'message', 'to': 'worker0', 'text': 'Will you apply?'}])
        self.market.submit(packet)
        path = self.market.root/'events.jsonl'; original = path.read_bytes()
        self.market.submit(packet)
        self.assertEqual(path.read_bytes(), original)
        self.market.submit(self.packet('client1', [{'id': 'pass', 'action': 'pass'}]))
        self.assertTrue(path.read_bytes().startswith(original))
        self.assertEqual(len(self.market.state['messages']), 1)

    def test_wrong_actor_day_and_prompt_blocked(self):
        with self.assertRaises(ValueError): self.market.brief('worker0')
        packet = self.packet('client0', [])
        packet['day'] = 2
        with self.assertRaises(ValueError): self.market.submit(packet)
        packet['day'] = 1; packet['prompt'] += 'tampered'
        with self.assertRaises(ValueError): self.market.submit(packet)
        with self.assertRaises(ValueError): self.market.advance()

    def test_duplicate_command_cannot_mutate_or_repeat(self):
        command = {'id': 'one', 'action': 'message', 'to': 'worker0', 'text': 'Hello'}
        self.market.command('client0', command); self.market.command('client0', command)
        self.assertEqual(len(self.market.state['messages']), 1)
        with self.assertRaises(ValueError): self.market.command('client0', {**command, 'text': 'different'})

    def test_unpaid_wage_never_marked_paid(self):
        self.market.command('client0', {'id': 'post', 'action': 'post_job', 'job_id': 'J1',
                  'title': 'Write a menu', 'description': 'Write three readable menu descriptions.', 'amount_micro': 100000})
        job = self.market.state['jobs']['J1']
        job.update(status='reviewed', worker='worker0', reviews=[{'accepted': True}])
        result = self.market.command('client0', {'id': 'pay', 'action': 'propose_payment', 'job_id': 'J1'})
        self.assertEqual(job['status'], 'payment_pending')
        self.assertEqual(self.market.state['confirmed']['worker_wages_micro'], 0)
        self.assertEqual(result['status'], 'pending_chain')
        # An untrusted flag is not evidence and is rejected before changing accounting.
        with self.assertRaises((ValueError, KeyError)):
            self.market.import_receipt({'intent_id': result['intent_id'], 'verified': True}, lambda m,p:'0x14a34')
        self.assertEqual(job['status'], 'payment_pending')

    def test_work_requires_chain_open(self):
        self.market.command('client0', {'id': 'post', 'action': 'post_job', 'job_id': 'J1',
                 'title': 'Menu', 'description': 'Three descriptions', 'amount_micro': 100000})
        self.market.state['jobs']['J1'].update(worker='worker0', status='guarantee_pending')
        with self.assertRaises(ValueError):
            self.market.command('worker0', {'id': 'work', 'action': 'deliver', 'job_id': 'J1', 'text': 'Artifact'})

    def test_funding_and_daily_barriers(self):
        self.market.command('sponsor0', {'id': 'fund', 'action': 'propose_funding', 'amount_micro': 100000})
        self.market.state['status'] = 'awaiting_daily_chain_reconciliation'
        self.market.state['turn'] = 100
        with self.assertRaises(ValueError): self.market.advance()
        intent = next(iter(self.market.state['intents']))
        self.market.reject_intent(intent, 'RPC unavailable; no execution occurred')
        self.market.advance()
        self.assertEqual(self.market.state['day'],2)
        self.assertTrue(self.market.state['bootstrap_barrier'])

    def test_spoof_semantics_and_readback_cannot_confirm(self):
        result = self.market.command('sponsor0', {'id':'fund','action':'propose_funding','amount_micro':100000})
        intent = self.market.state['intents'][result['intent_id']]
        proof = {'intent_id': intent['id'], 'verified': True, 'transaction_hash': '0x'+'2'*64,
                 'expected_calldata': '0x12345678', 'adapter_source':'fabricated',
                 'semantic_evidence': {'kind':intent['kind'],'payload':intent['payload']},
                 'readbacks':[{'purpose':'token_binding','expected':TOKEN},{'purpose':'intent_outcome','expected':'0x01'}]}
        with self.assertRaisesRegex(ValueError, 'disabled'):
            self.market.import_receipt(proof, lambda m,p: '0x01')
        self.assertEqual(intent['status'],'pending')
        self.assertEqual(self.market.state['confirmed']['sponsor_funding_micro'],0)

    def test_roster_actors_format_and_private_isolation(self):
        packet = {'actors':[{'id':p['id'],'role':p['role'],'public':{'name':p['name']},
                            'private':{'secret':p['private_brief']}} for p in self.characters]}
        source = self.root/'actors.json'; source.write_text(json.dumps(packet))
        market = Market.init(self.root/'actors-run',source)
        prompt = market.brief('client0')
        self.assertIn('PRIVATE-client-0',prompt); self.assertNotIn('PRIVATE-worker-0',prompt)

    def test_no_guarantee_without_client_hire_and_worker_acceptance(self):
        self.market.command('client0', {'id':'post','action':'post_job','job_id':'J1',
                    'title':'Menu','description':'Write synthetic menu','amount_micro':100000})
        self.market.command('worker0', {'id':'apply','action':'apply','job_id':'J1','text':'I volunteer'})
        with self.assertRaisesRegex(ValueError,'client hire'):
            self.market.command('issuer0', {'id':'open','action':'propose_guarantee','job_id':'J1',
                             'worker_id':'worker0','amount_micro':30000})
        self.market.command('client0', {'id':'hire','action':'hire','job_id':'J1','worker_id':'worker0','text':'Terms'})
        self.market.command('worker0', {'id':'accept','action':'accept_terms','job_id':'J1','text':'I agree to these terms'})
        with self.assertRaisesRegex(ValueError,'reserve funding'):
            self.market.command('issuer0', {'id':'open','action':'propose_guarantee','job_id':'J1',
                             'worker_id':'worker0','amount_micro':30000})

    def test_changed_hire_invalidates_old_worker_acceptance(self):
        self.market.command('client0', {'id':'post','action':'post_job','job_id':'J1',
                  'title':'Menu','description':'Write synthetic menu','amount_micro':100000})
        self.market.command('worker0', {'id':'apply','action':'apply','job_id':'J1','text':'I volunteer'})
        self.market.command('client0', {'id':'hire1','action':'hire','job_id':'J1','worker_id':'worker0','text':'Three lines'})
        self.market.command('worker0', {'id':'accept','action':'accept_terms','job_id':'J1','text':'Accepted'})
        old = self.market.state['jobs']['J1']['hire_terms_hash']
        self.market.command('client0', {'id':'hire2','action':'hire','job_id':'J1','worker_id':'worker0','text':'Thirty lines'})
        self.assertNotEqual(old,self.market.state['jobs']['J1']['hire_terms_hash'])
        self.assertNotIn('worker_acceptance',self.market.state['jobs']['J1'])
        with self.assertRaisesRegex(ValueError,'client hire'):
            self.market.command('issuer0', {'id':'open','action':'propose_guarantee','job_id':'J1',
                         'worker_id':'worker0','amount_micro':30000})

    def test_missing_fresh_context_provenance_is_refused(self):
        packet = self.packet('client0',[]); packet.pop('model_context')
        with self.assertRaisesRegex(ValueError,'provenance'): self.market.submit(packet)

    def test_all_sponsors_may_decline_and_zero_reserve_day_advances(self):
        for actor in self.market.state['queue']:
            self.market.submit(self.packet(actor,[{'id':'day1-pass','action':'pass','text':'No commitment today.'}]))
        self.assertEqual(len(self.market.state['turn_receipts']),100)
        self.assertEqual(self.market.state['confirmed']['sponsor_funding_micro'],0)
        self.assertTrue(self.market.state['bootstrap_barrier'])
        self.market.advance()
        self.assertEqual(self.market.state['day'],2)
        self.assertEqual(self.market.next_actor(),'client0')
        brief=self.market.brief('client0')
        self.assertIn('"role_wallet_bootstrap_verified":true',brief)
        self.assertIn('"confirmed_reserve_funding_micro":0',brief)
        self.assertIn('"reserve_funding_barrier":true',brief)

    def test_day_advance_still_requires_verified_wallet_bootstrap(self):
        self.market.state['status']='awaiting_daily_chain_reconciliation'
        self.market.state['turn']=100
        self.market.state.pop('verified_wallet_bootstrap')
        with self.assertRaisesRegex(ValueError,'role-wallet bootstrap'):self.market.advance()
        self.assertEqual(self.market.state['day'],1)

    def test_zero_reserve_still_refuses_guarantees(self):
        self.market.command('client0',{'id':'post','action':'post_job','job_id':'J1',
                   'title':'Menu','description':'Write a menu','amount_micro':100000})
        self.market.command('worker0',{'id':'apply','action':'apply','job_id':'J1','text':'Apply'})
        self.market.command('client0',{'id':'hire','action':'hire','job_id':'J1','worker_id':'worker0','text':'Terms'})
        self.market.command('worker0',{'id':'accept','action':'accept_terms','job_id':'J1','text':'Accept'})
        command={'id':'open','action':'propose_guarantee','job_id':'J1','worker_id':'worker0','amount_micro':30000}
        with self.assertRaisesRegex(ValueError,'reserve funding'):self.market.command('issuer0',command)
        self.market.state['bootstrap_barrier']=False  # stale barrier cannot authorize zero funded reserve
        with self.assertRaisesRegex(ValueError,'exposure cap'):self.market.command('issuer0',command)
        self.assertEqual(self.market.state['jobs']['J1']['status'],'proposed')
        self.assertFalse(self.market.state['intents'])

    def test_role_order(self):
        roles = [self.market.personas[a]['role'] for a in self.market.state['queue']]
        self.assertEqual(roles, ['client']*40 + ['backer']*14 + ['sponsor']*4 + ['worker']*40 + ['issuer','adjudicator'])

if __name__ == '__main__': unittest.main()
