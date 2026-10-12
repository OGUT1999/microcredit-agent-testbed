export const meta = {
  name: 'gt-sim-group',
  description: 'One group of fictional personas acts for one simulated day in the GuaranteeTrust sandbox (test tokens on a local fork)',
  phases: [{ title: 'Act' }],
}
const SCHEMA = { type: 'object', properties: { summary: { type: 'string' }, notable: { type: 'string' } }, required: ['summary', 'notable'] }
const instr = a => `Your complete instructions are in the file ${a.file}. Read that file with the Read tool first, then follow it exactly. Read no other file.`
const run = a => agent(instr(a), { label: a.label, phase: 'Act', schema: SCHEMA, model: 'opus' }).then(r => ({ name: a.name, role: a.role, ...(r || {}) }))
const first = args.agents.filter(a => a.role !== 'worker')
const second = args.agents.filter(a => a.role === 'worker')
const r1 = await parallel(first.map(a => () => run(a)))
const r2 = await parallel(second.map(a => () => run(a)))
return [...r1, ...r2].filter(Boolean)