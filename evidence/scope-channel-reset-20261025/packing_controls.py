"""Facilitator-only, hand-authored synthetic controls. Not a participant scorer."""
from packing_packet import answer, render_reader

# Deliberately typed from the review's independent oracle, not generated from answer().
FAITHFUL_NOTES = '''A1 packed 3; remaining 2; hold no
A2 packed 2; remaining 0; hold no
B1 packed unknown; remaining unknown; hold no
B2 packed 0; remaining 3; hold yes
C1 packed 3; remaining 3; hold yes
C2 packed 2; remaining 0; hold no
D1 packed 3; remaining 0; hold no
D2 packed 1; remaining 0; hold no'''
FLAWED_NOTES = '''A1 packed 3; remaining 2; hold no
A2 packed 2; remaining 0; hold no
B1 packed 4; remaining 0; hold no
B2 packed 0; remaining 3; hold yes
C1 packed 3; remaining 3; hold yes
C2 packed 2; remaining 0; hold no
D1 packed 3; remaining 0; hold no
D2 packed 1; remaining 0; hold no'''
FAITHFUL_LEDGER = '''A1 | 3 | 2 | no
A2 | 2 | 0 | no
B1 | unknown | unknown | no
B2 | 0 | 3 | yes
C1 | 3 | 3 | yes
C2 | 2 | 0 | no
D1 | 3 | 0 | no
D2 | 1 | 0 | no'''

def parse_control(text, style):
    import re
    pattern = (r'(\w+) packed (\w+); remaining (\w+); hold (yes|no)'
               if style == 'notes' else r'(\w+) \| (\w+) \| (\w+) \| (yes|no)')
    out = {}
    for line in text.splitlines():
        m = re.fullmatch(pattern, line)
        if not m: raise ValueError('Malformed bundled control')
        code, packed, remaining, hold = m.groups()
        if code in out: raise ValueError('Duplicate control line')
        out[code] = {'packed': None if packed == 'unknown' else int(packed),
                     'remaining': None if remaining == 'unknown' else int(remaining),
                     'hold': hold == 'yes'}
    return out

def errors(text, style):
    actual = parse_control(text, style)
    expected = answer('X')
    if set(actual) != set(expected): raise ValueError('Missing or extra control lines')
    return {code: [field for field in ('packed','remaining','hold')
                   if actual[code][field] != (bool(expected[code][field]) if field == 'hold'
                                              else expected[code][field])]
            for code in expected if any(actual[code][field] !=
                 (bool(expected[code][field]) if field == 'hold' else expected[code][field])
                 for field in ('packed','remaining','hold'))}

def reader_boundary_ok(text, condition):
    # Exact fixture boundary, deliberately not a generic semantic leak detector.
    # A changed reader fixture requires review and a corresponding updated check.
    return text == render_reader(condition)

if __name__ == '__main__':
    import json
    print(json.dumps({'faithful_notes': errors(FAITHFUL_NOTES,'notes'),
                      'lost_uncertainty_notes': errors(FLAWED_NOTES,'notes'),
                      'faithful_ledger': errors(FAITHFUL_LEDGER,'ledger')}, indent=2))
