"""Offline teaching example only. No files, network, or live Kobo access.

Synthetic choices illustrate why an unversioned lookup is not a safe repair.
This is not Kobo's export implementation and does not diagnose a user's data.
"""
import json
from copy import deepcopy

CHOICES = [
    {'version': 'example_v1', 'code': 's1', 'label': 'Example School A', 'parent': 'w1'},
    {'version': 'example_v2', 'code': 's1', 'label': 'Example School B', 'parent': 'w2'},
    {'version': 'example_v2', 'code': 'dup', 'label': 'Example School C', 'parent': 'w2'},
    {'version': 'example_v2', 'code': 'dup', 'label': 'Example School D', 'parent': 'w3'},
]
CASES = [
    {'case': 'old_version', 'version': 'example_v1', 'code': 's1', 'parent': 'w1'},
    {'case': 'new_version', 'version': 'example_v2', 'code': 's1', 'parent': 'w2'},
    {'case': 'unknown_version', 'version': 'example_v3', 'code': 's1', 'parent': 'w1'},
    {'case': 'missing_version', 'version': '', 'code': 's1', 'parent': 'w1'},
    {'case': 'unknown_code', 'version': 'example_v2', 'code': 's9', 'parent': 'w2'},
    {'case': 'duplicate_key', 'version': 'example_v2', 'code': 'dup', 'parent': 'w2'},
    {'case': 'parent_mismatch', 'version': 'example_v2', 'code': 's1', 'parent': 'w1'},
]

def inspect_example(row, choices):
    """Return an annotation, never alter the original or guess a correction."""
    out = {'case': row['case'], 'original': deepcopy(row), 'status': None, 'label': None}
    if not row.get('version'):
        out['status'] = 'UNRESOLVED_MISSING_VERSION'
        return out
    versions = {choice['version'] for choice in choices}
    if row['version'] not in versions:
        out['status'] = 'UNRESOLVED_UNKNOWN_VERSION'
        return out
    matches = [c for c in choices if (c['version'], c['code']) == (row['version'], row['code'])]
    if not matches:
        out['status'] = 'UNRESOLVED_UNKNOWN_CODE'
    elif len(matches) != 1:
        out['status'] = 'UNRESOLVED_DUPLICATE_KEY'
    elif matches[0]['parent'] != row['parent']:
        out['status'] = 'UNRESOLVED_PARENT_MISMATCH'
    else:
        out['status'] = 'CONSISTENT_WITH_SYNTHETIC_DICTIONARY'
        out['label'] = matches[0]['label']
    return out

if __name__ == '__main__':
    print(json.dumps([inspect_example(r, CHOICES) for r in CASES], indent=2))
