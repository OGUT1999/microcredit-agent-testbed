import unittest
from copy import deepcopy
from synthetic_mapping import CASES, CHOICES, inspect_example

class SyntheticExampleTests(unittest.TestCase):
    def test_version_disambiguates_reused_code(self):
        self.assertEqual(inspect_example(CASES[0], CHOICES)['label'], 'Example School A')
        self.assertEqual(inspect_example(CASES[1], CHOICES)['label'], 'Example School B')
        naive_latest_lookup = {c['code']: c['label'] for c in CHOICES}
        self.assertNotEqual(naive_latest_lookup[CASES[0]['code']], 'Example School A')

    def test_uncertainty_never_emits_a_repair(self):
        expected = ['UNRESOLVED_UNKNOWN_VERSION', 'UNRESOLVED_MISSING_VERSION',
                    'UNRESOLVED_UNKNOWN_CODE', 'UNRESOLVED_DUPLICATE_KEY',
                    'UNRESOLVED_PARENT_MISMATCH']
        for row, status in zip(CASES[2:], expected):
            with self.subTest(case=row['case']):
                result = inspect_example(row, CHOICES)
                self.assertEqual(result['status'], status)
                self.assertIsNone(result['label'])

    def test_inputs_and_original_annotations_unchanged(self):
        rows, choices = deepcopy(CASES), deepcopy(CHOICES)
        outputs = [inspect_example(r, CHOICES) for r in CASES]
        self.assertEqual(CASES, rows)
        self.assertEqual(CHOICES, choices)
        self.assertEqual([r['original'] for r in outputs], rows)
        outputs[0]['original']['code'] = 'changed-output-only'
        self.assertEqual(CASES, rows)

    def test_order_does_not_resolve_ambiguous_keys(self):
        for row in CASES:
            self.assertEqual(inspect_example(row, CHOICES), inspect_example(row, list(reversed(CHOICES))))

if __name__ == '__main__':
    unittest.main()
