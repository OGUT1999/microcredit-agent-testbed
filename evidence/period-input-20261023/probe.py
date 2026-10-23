import json,itertools
from openfisca_core import periods
rows=[]
for unit,day in itertools.product(['month','year'],[1,2,12,28]):
 s=f'{unit}:2015-09-{day:02d}';a=periods.period(s);b=periods.period(str(a));rows.append({'input':s,'serialized':str(a),'same_period':a==b,'original_start':str(a.start),'roundtrip_start':str(b.start)})
print(json.dumps(rows,indent=2))
assert all(r['same_period']==r['input'].endswith('-01') for r in rows)
