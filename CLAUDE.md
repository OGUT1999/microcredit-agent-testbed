# Working in the testbed

Read [AGENTS.md](AGENTS.md) first, especially its work-cycle questions, then
[NORTH_STAR.md](coordination/NORTH_STAR.md), the current
[world model](world-model/model.json), and the shared
[team operating guide](coordination/README.md). Do not maintain a competing
strategy or backlog here.

For every substantive deliverable, state the measurable human outcome or decision,
the evidence sought, the competing simpler route, and the stop/change condition.
Credit is provisional. The current lending-specific test is the exact qualification
predicate in NORTH_STAR.md; **NONE QUALIFIES is a successful measurement**, not a
reason to broaden outreach until a loan case appears. Broad 501(c)(3) discovery for
direct project support is exhausted absent a new specific lead.

Run `python tools/check.py` before submitting changes. It covers maintained
code and schema checks without importing live experiments or rewriting evidence.
Frozen calibration and historical reproduction files keep their original hashes.
