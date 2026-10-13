export const meta = {
  name: 'gt-sim-roles',
  description: 'The issuer and then the adjudicator personas act for one simulated day in the GuaranteeTrust sandbox (test tokens on a local fork)',
  phases: [{ title: 'Roles' }],
}
const SCHEMA = { type: 'object', properties: { summary: { type: 'string' }, notable: { type: 'string' } }, required: ['summary', 'notable'] }
const instr = a => `Your complete instructions are in the file ${a.file}. Read that file with the Read tool first, then follow it exactly. Read no other file. You may run up to 70 commands today if your role needs it.`
const out = []
for (const a of args.agents) {
  const r = await agent(instr(a), { label: a.label, phase: 'Roles', schema: SCHEMA, model: 'opus' })
  out.push({ name: a.name, role: a.role, ...(r || {}) })
}
return out
