# Controller recovery — 2026-10-12

This directory is a lossless recovery point for north-star controller artifacts created locally while GitHub publication was unavailable or blocked.

The canonical current project state remains `world-model/model.json`. Older artifacts here are provenance and may contain intermediate hypotheses or illustrative numbers that later canonical decisions supersede.

The exact local recovery archive had SHA-256:

`4f37a7ec01d8f9b07bf07f7058c7eea5aaa794fbeb3c2a096c2871788bb9dad2`

It is stored as ordered base64 text parts under `archive/`. Reconstruct with:

```bash
cat archive/part-*.b64 | base64 -d > controller_recovery_2026-10-12.tar.gz
sha256sum controller_recovery_2026-10-12.tar.gz
tar -xzf controller_recovery_2026-10-12.tar.gz
```

The archive preserves the exact local files; `MANIFEST.md` records hashes and canonicalization notes; `RECOVERY_LEDGER.md` summarizes the substantive findings and how they relate to model versions 0.1.100–0.1.103.
