import unittest
from pathlib import Path
from packing_packet import render_reader, fixture, answer
from packing_controls import (FAITHFUL_NOTES, FLAWED_NOTES, FAITHFUL_LEDGER,
                              errors, reader_boundary_ok)

class HandoffControlTests(unittest.TestCase):
    def test_reader_side_distinguishes_lost_uncertainty(self):
        self.assertEqual(errors(FAITHFUL_NOTES,'notes'), {})
        self.assertEqual(errors(FAITHFUL_LEDGER,'ledger'), {})
        self.assertEqual(errors(FLAWED_NOTES,'notes'), {'B1':['packed','remaining']})

    def test_reader_boundary_rejects_actual_contamination(self):
        root=Path(__file__).parent
        for condition in ('notes','ledger'):
            actual=(root/f'packing-X-reader-{condition}.md').read_text()
            self.assertTrue(reader_boundary_ok(actual,condition))
            for contamination in ('\n'+FAITHFUL_NOTES,
                                  '\n'+(root/'packing-X-notes.md').read_text(),
                                  '\n'+(root/'packing-facilitator-key.md').read_text()):
                self.assertFalse(reader_boundary_ok(actual+contamination,condition))
            self.assertNotIn('place 4 units',actual)
            self.assertNotIn('Supplier quantity disputed',actual)
            self.assertNotIn('B1 must be unknown',actual)

    def test_y_is_predictable_and_is_not_an_independent_arm(self):
        # Explicitly retain the falsifier; do not claim shuffled cards fix carryover.
        x,y=answer('X'),answer('Y')
        mapped={chr(ord(c[0])+4)+c[1:]:
                {k:(2*v if type(v) is int else v) for k,v in row.items()}
                for c,row in x.items()}
        self.assertEqual(mapped,y)
        guide=(Path(__file__).parent/'packing-packet-guide.md').read_text()
        self.assertIn('NOT an independent form or crossover arm',guide)
        self.assertIn('use one condition per participant/team and form X only',guide)

if __name__ == '__main__': unittest.main()
