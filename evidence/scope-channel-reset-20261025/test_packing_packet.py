import json
from pathlib import Path
import unittest
from packing_packet import answer, fixture, render

class PackingPacketTests(unittest.TestCase):
    def test_hand_calculated_oracle(self):
        expected = {'A1': (3, 2, False), 'A2': (2, 0, True),
                    'B1': (None, None, False), 'B2': (0, 3, False),
                    'C1': (3, 3, False), 'C2': (2, 0, True),
                    'D1': (3, 0, True), 'D2': (1, 0, True)}
        actual = answer('X')
        self.assertEqual({k: (v['packed'], v['remaining'], v['packed_complete'])
                          for k, v in actual.items()}, expected)
        self.assertEqual({k for k,v in actual.items() if v['hold']}, {'B2','C1'})
        # Both D lines complete, but this is still not shipment evidence.
        self.assertEqual({k[0] for k in actual if all(v['packed_complete']
                         for c,v in actual.items() if c[0] == k[0])}, {'D'})

    def test_add_only_shortcut_is_wrong(self):
        # Demonstrates a failure mode, not a fair human-baseline performance claim.
        _, events = fixture('X')
        totals = {c: sum(n for code, kind, n in events if code == c and kind == 'add')
                  for c, _ in fixture('X')[0]}
        self.assertNotEqual(totals['A1'], answer('X')['A1']['packed'])
        self.assertNotEqual(totals['D1'], answer('X')['D1']['packed'])
        self.assertIsNone(answer('X')['B1']['packed'])

    def test_information_parity_and_no_answer_leak(self):
        for form in ('X','Y'):
            a, b = render(form,'notes'), render(form,'ledger')
            # Everything from initial state through events is identical.
            self.assertEqual(a.split('AI-authored',1)[1].split('## Working area')[0],
                             b.split('AI-authored',1)[1].split('## Working area')[0])
            self.assertEqual(a.split('## Handoff questions')[1],b.split('## Handoff questions')[1])
            self.assertIn('first letter of a line ID identifies its order', a)
            self.assertNotIn('packed_complete', a+b)
            self.assertNotIn('fully packed: D', a+b)
            self.assertIn('ledger if that is the normal workaround', a)

    def test_matched_forms_preserve_logic_not_claimed_difficulty(self):
        x, y = answer('X'), answer('Y')
        for (cx,sx),(cy,sy) in zip(x.items(),y.items()):
            self.assertEqual(ord(cy[0])-ord(cx[0]),4)
            for key in ('packed','remaining','required'):
                self.assertEqual(sy[key], None if sx[key] is None else 2*sx[key])
            self.assertEqual(sx['packed_complete'],sy['packed_complete'])
            self.assertEqual(sx['hold'],sy['hold'])

    def test_committed_packets_match_generator(self):
        root=Path(__file__).parent
        for form in ('X','Y'):
            for condition in ('notes','ledger'):
                self.assertEqual((root/f'packing-{form}-{condition}.md').read_text(),render(form,condition))
        self.assertEqual(json.loads((root/'packing-answer-key.json').read_text()),
                         {f:answer(f) for f in ('X','Y')})

if __name__ == '__main__': unittest.main()
