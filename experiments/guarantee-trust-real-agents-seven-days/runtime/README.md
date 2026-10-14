# Isolated preparation runtime

This is a **new** dependency resolution created on 2026-10-13 from the official
npm registry, not the lost historical runtime. It pins ethers **6.15.0** and its
eight transitive packages in `package-lock.json` (npm lockfile version 3).
Other project package files and dependencies are unchanged.

From the repository root:

```bash
npm ci --prefix experiments/guarantee-trust-real-agents-seven-days/runtime --ignore-scripts --no-audit --no-fund --registry=https://registry.npmjs.org
python experiments/guarantee-trust-real-agents-seven-days/offline-check.py
```

Use the environment's existing authorized network/proxy configuration; do not
change persistent npm, credential, network or security settings. `npm ci`
uses the frozen graph; do not replace it with an unpinned install or upgrade.
The initial preparation used Node v24.19.0 and npm 11.9.0. The disabled workflow
specifies Node 22, whose runtime compatibility has not been revalidated here.

Before installation, every resolved package's official registry metadata was
checked against the lock's tarball URL and SHA512 integrity. No published
lifecycle scripts were present. Installation used `--ignore-scripts`; all nine
installed versions matched the lock and their installed manifests also had no
lifecycle scripts. See `dependency-review.json` for versions and provenance.
The lockfile did not change during `npm ci`. `node_modules` is ignored.

The offline checker copies the executor's exact bytes into a disposable child
directory here so Node can resolve this runtime's ethers. It invokes only
`--validate`, which exits before provider or wallet construction. The temporary
copy is removed afterward. No symlink, live entrypoint, workflow or other
project's module resolution is changed. Do not run the executor without this
metadata-only flag as part of these preparation checks.

Executor `--self-test` is deliberately excluded because it creates a random
wallet and signs typed data. Metadata and fixture checks are not EVM rehearsal,
independent review, proof of custody safety or authorization for live execution.
