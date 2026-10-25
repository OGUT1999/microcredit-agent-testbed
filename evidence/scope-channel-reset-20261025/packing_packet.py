"""Generate invented paper exercises only; no user data, network or live operations."""
from pathlib import Path
import json

# These are teaching fixtures, not a representative sample of food hubs.
ROWS = [('A1', 5), ('A2', 2), ('B1', 4), ('B2', 3),
        ('C1', 6), ('C2', 2), ('D1', 3), ('D2', 1)]
EVENTS = [
    ('A1', 'add', 4), ('A2', 'add', 2), ('B1', 'add', 4),
    ('B2', 'hold', 'Supplier quantity disputed'), ('C1', 'add', 3),
    ('C2', 'add', 2), ('D1', 'add', 3), ('D2', 'add', 1),
    ('A1', 'remove', 1), ('C1', 'hold', 'Contents require operator check'),
    ('D1', 'remove', 1), ('D1', 'add', 1),
    ('D2', 'hold', 'Line identity disputed'),
    ('D2', 'clear', 'Operator resolved identity dispute'),
    ('B1', 'unknown', 'Unrecorded change reported; present quantity not known'),
]

def fixture(form):
    if form not in ('X', 'Y'):
        raise ValueError('Only bundled invented forms X and Y exist')
    # Matched logical structure, not empirical equivalence. Scaling does not
    # establish equal difficulty. A participant must never see both answer keys.
    factor = 1 if form == 'X' else 2
    rename = lambda code: code if form == 'X' else chr(ord(code[0]) + 4) + code[1:]
    rows = [(rename(code), n * factor) for code, n in ROWS]
    events = [(rename(code), kind, value * factor if isinstance(value, int) else value)
              for code, kind, value in EVENTS]
    return rows, events

def answer(form):
    rows, events = fixture(form)
    state = {code: {'required': n, 'packed': 0, 'hold': None} for code, n in rows}
    for code, kind, value in events:
        s = state[code]
        if kind in ('add', 'remove'):
            if s['packed'] is not None:
                s['packed'] += value if kind == 'add' else -value
        elif kind == 'hold':
            s['hold'] = value
        elif kind == 'clear':
            s['hold'] = None
        elif kind == 'unknown':
            s['packed'] = None
    for s in state.values():
        s['remaining'] = None if s['packed'] is None else s['required'] - s['packed']
        s['packed_complete'] = s['packed'] == s['required'] and s['hold'] is None
    return state

def event_text(event):
    code, kind, value = event
    if kind == 'add': return f'{code}: place {value} units in the order container.'
    if kind == 'remove': return f'{code}: remove {value} units from the order container.'
    if kind == 'hold': return f'{code}: unresolved exception: {value}.'
    if kind == 'clear': return f'{code}: exception cleared: {value}.'
    return f'{code}: {value}.'

def render(form, condition):
    if condition not in ('notes', 'ledger'): raise ValueError('Unknown condition')
    rows, events = fixture(form)
    text = [f'# Invented packing exercise — form {form}, {condition}', '',
            'AI-authored internal draft. Not an order, food-handling instruction or approved field test.', '',
            'The first letter of a line ID identifies its order (for example, A1 and A2 belong to order A).',
            'Each line begins with zero units packed and no exception. Required quantities stay fixed.',
            'All shipments are unchanged and unshipped. There are no customer/carrier handoffs.',
            'A numerical remainder is not evidence of stock availability. Unknown means do not guess.', '',
            '## Starting sheet', '', '| Line | Required units |', '| --- | ---: |']
    text += [f'| {code} | {n} |' for code, n in rows]
    text += ['', '## Event cards (same information in both conditions)', '']
    text += [f'{i}. {event_text(e)}' for i, e in enumerate(events, 1)]
    text += ['', '## Working area', '']
    if condition == 'notes':
        text += ['Use ordinary notes, tally marks, a table or any familiar paper method.',
                 'Do not prohibit a ledger if that is the normal workaround.', '',
                 '\n'.join(['Notes: _____________________________________________________'] * 8)]
    else:
        text += ['Optional structure; ordinary notes remain allowed. Fill from the same events.', '',
                 '| Line | Packed now or unknown | Remaining or unknown | Unresolved exception |',
                 '| --- | --- | --- | --- |']
        text += [f'| {code} | ______ | ______ | __________________ |' for code, _ in rows]
    text += ['', '## Handoff questions', '',
             'For each line record current packed quantity, remaining quantity (or unknown), and unresolved exception.',
             'Which orders are fully packed with no unresolved exception? What establishes shipment?',
             'Mark uncertainty explicitly. Do not resolve a supplier/contents question from this exercise.', '',
             'Recorder time: ____  Reader time: ____  Clarification requests: ____',
             'This sheet contains no answer key. Timing fields are blank, not measurements.', '']
    return '\n'.join(text)

if __name__ == '__main__':
    root = Path(__file__).parent
    for form in ('X', 'Y'):
        for condition in ('notes', 'ledger'):
            (root / f'packing-{form}-{condition}.md').write_text(render(form, condition))
    (root / 'packing-answer-key.json').write_text(json.dumps({f: answer(f) for f in ('X', 'Y')}, indent=2) + '\n')
