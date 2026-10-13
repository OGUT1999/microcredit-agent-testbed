/**
 * Circle test-USDC cold-start adaptation of the GPT 100-character experiment.
 * Policy characters are internally controlled deterministic policies, not LLMs.
 * Only Base Sepolia (84532) is allowed; this is not economic-impact evidence.
 * No private keys, signatures or signed transaction bytes are written or printed.
 * Usage: node coldstart.mjs --validate | node coldstart.mjs
 * Needs ethers 6.15.0 and the exact reviewed Foundry artifact at ./artifact.json.
 */
import {
  Contract, ContractFactory, JsonRpcProvider, NonceManager, Wallet, ZeroHash,
  formatEther, formatUnits, getAddress, keccak256, parseEther, parseUnits, TypedDataEncoder, zeroPadValue, toBeHex,
  toUtf8Bytes, version, hexlify, zeroPadBytes,
} from 'ethers';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const SOURCE = 'ec93c76779b5e2d52ab7b87cf82b3fd400205969';
const REHEARSAL = process.env.REHEARSAL === '1';
const RPC = process.env.RPC_URL || process.env.COLDSTART_RPC || 'https://sepolia.base.org';
if (REHEARSAL && !['localhost', '127.0.0.1', '[::1]'].includes(new URL(RPC).hostname)) {
  throw Error('Rehearsal is restricted to localhost RPC');
}
if (!REHEARSAL && process.env.TEST_TOKEN_ADDRESS) throw Error('Token override requires a localhost rehearsal');
if (!REHEARSAL && process.env.REHEARSAL_STOP_AFTER_LABEL) throw Error('A debug stop requires a localhost rehearsal');
const TOKEN = getAddress(REHEARSAL && process.env.TEST_TOKEN_ADDRESS
  ? process.env.TEST_TOKEN_ADDRESS : '0x036CbD53842c5426634e7929541eC2318f3dCF7e');
const EXPECT_ROOT = REHEARSAL && process.env.TEST_WALLET_PRIVATE_KEY
  ? new Wallet(process.env.TEST_WALLET_PRIVATE_KEY).address
  : getAddress('0x38e9845A1Df22c59Bfc693bf2CEAa3361158d6d1');
const SEED = 20261013;
const ROUNDS = 24;
const U = 1_000_000n;
const u = x => parseUnits(String(x), 6);
const sha = x => createHash('sha256').update(x).digest('hex');
const hash = x => keccak256(toUtf8Bytes(JSON.stringify(x)));
const serial = x => JSON.parse(JSON.stringify(x, (_, v) => typeof v === 'bigint' ? v.toString() : v));
const artifactPath = process.env.COLDSTART_ARTIFACT || path.join(HERE, 'artifact.json');
const artifactBytes = fs.readFileSync(artifactPath);
const artifact = JSON.parse(artifactBytes);
const bytecode = typeof artifact.bytecode === 'string' ? artifact.bytecode : artifact.bytecode.object;
const runtime = typeof artifact.deployedBytecode === 'string' ? artifact.deployedBytecode : artifact.deployedBytecode.object;
if (!bytecode?.startsWith('0x') || !runtime?.startsWith('0x') || !Array.isArray(artifact.abi)) {
  throw Error('Reviewed artifact missing bytecode, deployed bytecode or ABI');
}
if (version !== '6.15.0') throw Error('Expected ethers 6.15.0');

function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6D2B79F5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const rng = mulberry32(SEED);
const pad = x => String(x).padStart(2, '0');
const clients = Array.from({length: 40}, (_, i) => ({
  id: `client-${pad(i + 1)}`, role: 'client',
  groupId: hash({experiment: 'circle-coldstart-v1', group: i + 1}),
  clientId: hash({experiment: 'circle-coldstart-v1', client: i + 1}),
  postProbability: 0.34 + 0.035 * (i % 5),
  payProbability: 0.91 + 0.015 * (i % 4),
  wageLowTenths: 18 + 2 * (i % 3), wageHighTenths: 34 + 3 * (i % 4),
}));
const workers = Array.from({length: 40}, (_, i) => ({
  id: `worker-${pad(i + 1)}`, role: 'worker',
  qualityProbability: 0.90 + 0.015 * (i % 5),
}));
const backers = Array.from({length: 14}, (_, i) => ({
  id: `backer-${pad(i + 1)}`, role: 'backer',
  workers: [workers[2 * i].id, workers[2 * i + 1].id],
  laterStake: 0n,
}));
const sponsors = Array.from({length: 4}, (_, i) => ({id: `sponsor-${pad(i + 1)}`, role: 'sponsor', added: 0n}));
const personas = [...clients, ...workers, ...backers, ...sponsors];
const acceptanceTypes = {Acceptance: [
  ['worker', 'address'], ['clientId', 'bytes32'], ['groupId', 'bytes32'], ['amount', 'uint256'],
  ['maxFromDues', 'uint256'], ['termsHash', 'bytes32'], ['contributionBps', 'uint256'],
  ['contributionCap', 'uint256'], ['remitWindow', 'uint256'], ['settleBy', 'uint64'],
  ['holdUntil', 'uint64'], ['nonce', 'uint256'], ['deadline', 'uint256'],
].map(([name, type]) => ({name, type}))};
const consentTypes = {Consent: [
  ['member', 'address'], ['attester', 'address'], ['allowed', 'bool'], ['nonce', 'uint256'], ['deadline', 'uint256'],
].map(([name, type]) => ({name, type}))};
const manifest = {
  schema: 'guarantee-trust-circle-coldstart/1', sourceCommit: SOURCE,
  runnerSha256: sha(fs.readFileSync(fileURLToPath(import.meta.url))),
  artifactSha256: sha(artifactBytes), chainId: 84532, token: TOKEN, decimals: 6,
  rehearsal: REHEARSAL,
  policySeed: SEED, prng: 'mulberry32', rounds: ROUNDS, compressedRounds: true,
  roles: {clients: 40, workers: 40, backers: 14, sponsors: 4, issuer: 1, adjudicator: 1},
  policy: {
    reserveSeed: '2.0', sponsorTopupCap: '1.0', topupsStopAfterRound: 12,
    initialStakeEachBacker: '0.3', additionalStakeCapEach: '0.9', stakeAddsStopAfterRound: 12,
    initialBackingEachPair: '0.15', initialLines: '8 workers at 0.2; total 1.6',
    contributionBps: 500, contributionCap: '0.3', remitWindowSeconds: 86400,
    guarantee: '10% of synthetic wage, bounded to [0.2,0.8] test USDC',
    settlement: 'Immediate after admitted jobs. Undelivered work is cancelled; only delivered work followed by the client nonpayment draw is claimed.',
    wageAndContribution: 'Client pays gross wage minus signed contribution to worker; client remits the withheld contribution. Its total outflow equals the gross wage.',
    clientFundingEach: '20.0 test USDC from the operator test wallet',
    roleGasFundingEachETH: '0.00008', roleGasTotalCapETH: '0.005', rootGasUseCapETH: '0.03',
    onchainCaps: '20% single exposure;30% group; outstanding+G+2G<=reserve;one open/client',
  },
  gate: {window: [19, 24], noSponsorTopups: true, nonzeroThroughputEachRound: true,
    reserveNonshrinkingOverWindow: true, zeroReserveRuleRefusals: true, accountingIdentitiesEveryRound: true},
  caveats: [
    'Internally controlled deterministic policy characters, not independent LLM sessions or outside agents.',
    'A new contract-constrained onchain adaptation, not a numerical reproduction of the Python model.',
    'Client test wages and all initial role balances are internally prefunded; no external demand or revenue.',
    'Rounds are compressed policy steps, not 24 elapsed chain days.',
    'No real-value assets, work, independently earned human income or demonstrated human benefit.',
    'Owner, issuer and adjudicator authority are held by the same operator-controlled test wallet.',
    'Shutdown pauses origination and settles guarantees; dues and stake are retained and fully reported.',
  ],
  rationale: [
    'A zero-reserve control isolates the external first-funding requirement.',
    'Small seeded reserve and exclusive stake allocation obey Solidity constraints rather than fitting old aggregates.',
    'Job demand, quality and payment are seeded stochastic policies; admissibility and losses are determined by live contract state.',
    'Top-ups and new stakes stop after round 12; the final six-round gate cannot be bought with late sponsor funds.',
    'No desired outcome is enforced. A failed gate remains a failed result, with all positions settled.',
    'Outcomes emerge from policy draws and evolving contract balances, but policies, incentives and the population are authored internally.',
  ],
};
const iface = new ContractFactory(artifact.abi, bytecode).interface;
for (const name of ['openGuarantee', 'setConsentBySig', 'fundReserve', 'stake', 'attest', 'setLine',
  'setParams', 'markPaid', 'remit', 'claim', 'setPaused', 'guarantee', 'memberOf', 'capacity']) iface.getFunction(name);
if (!iface.getFunction('openGuarantee').inputs[0].components.some(x => x.name === 'holdUntil')) {
  throw Error('Artifact is not the reviewed r6 acceptance ABI');
}
if (process.argv.includes('--validate')) {
  console.log(JSON.stringify({validated: true, manifest, rosterCounts: personas.length + 2}, null, 2));
  process.exit(0);
}

const out = path.resolve(process.env.COLDSTART_OUT || path.join(HERE, 'coldstart-evidence'));
if (fs.existsSync(out) && fs.readdirSync(out).length > 0) throw Error('Evidence output directory is not empty; preserve it and choose a fresh directory');
fs.mkdirSync(out, {recursive: true});
if (fs.existsSync(path.join(out, 'checkpoint.json'))) throw Error('Existing execution checkpoint; inspect it before choosing a new output directory');
const write = (name, value) => {
  const p = path.join(out, name), tmp = `${p}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(serial(value), null, 2) + '\n'); fs.renameSync(tmp, p);
};
const append = (name, value) => fs.appendFileSync(path.join(out, name), JSON.stringify(serial(value)) + '\n');
const resumePath = process.env.COLDSTART_BOOTSTRAP_RESUME ? path.resolve(process.env.COLDSTART_BOOTSTRAP_RESUME) : null;
const priorPacket = resumePath ? {
  manifest: JSON.parse(fs.readFileSync(path.join(resumePath, 'manifest.json'))),
  checkpoint: JSON.parse(fs.readFileSync(path.join(resumePath, 'checkpoint.json'))),
  journal: JSON.parse(fs.readFileSync(path.join(resumePath, 'transactions.json'))),
  deployment: JSON.parse(fs.readFileSync(path.join(resumePath, 'prior-deployment.json'))),
  zero: JSON.parse(fs.readFileSync(path.join(resumePath, 'zero-reserve-control.json'))),
  recovery: fs.existsSync(path.join(resumePath, 'recovery.json'))
    ? JSON.parse(fs.readFileSync(path.join(resumePath, 'recovery.json'))) : null,
} : null;
if (priorPacket) {
  for (const field of ['sourceCommit', 'artifactSha256', 'chainId', 'token', 'rehearsal', 'policySeed', 'prng', 'rounds', 'roles', 'policy', 'gate']) {
    if (JSON.stringify(priorPacket.manifest[field]) !== JSON.stringify(manifest[field])) throw Error('Bootstrap resume policy or source differs from the prior execution');
  }
  if (priorPacket.manifest.rootAddress !== EXPECT_ROOT || priorPacket.checkpoint.round !== 0
    || !['deployed', 'funded'].includes(priorPacket.checkpoint.phase)) throw Error('Only a verified bootstrap stop may be resumed');
  if (fs.existsSync(path.join(resumePath, 'policy-events.jsonl')) && fs.readFileSync(path.join(resumePath, 'policy-events.jsonl'), 'utf8').trim()) {
    throw Error('Market-state resume is not supported');
  }
  if (priorPacket.journal.some(x => x.status !== 1)) throw Error('Prior journal contains an unconfirmed transaction requiring review');
}
const journal = priorPacket ? serial(priorPacket.journal.concat(priorPacket.recovery?.additionalConfirmedTransactions || [])) : [];
const confirmedLabels = new Map();
let rootFees = 0n, allFees = 0n, gasFunded = 0n, sponsorTopups = 0n, nextNonce = 1000n, lastMinedBlock;
let activeIntent = null;
const counts = {posted: 0, opened: 0, paid: 0, claimed: 0, cancelled: 0, remitted: 0, wages: 0n, netWages: 0n, contributions: 0n,
  claims: 0n, refusals: {}, laterStake: 0n};
const rounds = [];
const checkpoint = {sourceCommit: SOURCE, phase: 'preflight', round: 0,
  startedAtUTC: priorPacket?.checkpoint.startedAtUTC || new Date().toISOString(),
  ...(priorPacket ? {resumedAtUTC: new Date().toISOString(), bootstrapResume: true,
    priorRunnerSha256: priorPacket.manifest.runnerSha256, priorJournalCount: journal.length} : {})};
function saveCheckpoint() {write('checkpoint.json', checkpoint);}
async function freshRead(fn) {
  for (let attempt = 0; ; attempt++) {
    try {return await fn();} catch (e) {
      if (attempt >= 4) throw e;
      await new Promise(resolve => setTimeout(resolve, 500 * (attempt + 1)));
    }
  }
}
function errorCode(e) {return /^[A-Z0-9_]+$/.test(String(e?.code)) ? e.code : 'REDACTED_EXECUTION_FAILURE';}
const safeFailureMessages = new Set([...fs.readFileSync(fileURLToPath(import.meta.url), 'utf8').matchAll(/throw Error\('([^']+)'\)/g)].map(m => m[1]));
process.on('uncaughtException', e => stop(e));
process.on('unhandledRejection', e => stop(e));
function stop(e) {
  const safeReason = safeFailureMessages.has(e?.message) ? e.message : null;
  write('stopped.json', {atUTC: new Date().toISOString(), errorCode: errorCode(e), safeReason, checkpoint,
    transactionCount: journal.length, warning: 'Inspect mined/pending public hashes before any recovery; do not replay blindly.'});
  console.error(`STOPPED ${errorCode(e)} ${safeReason || ''}; evidence preserved in ${path.basename(out)}`);
  process.exit(1);
}
const rootKey = process.env.TEST_WALLET_PRIVATE_KEY;
if (!rootKey || !/^0x[0-9a-fA-F]{64}$/.test(rootKey)) throw Error('Funded test-wallet key is unavailable');
const provider = new JsonRpcProvider(RPC, undefined,
  {cacheTimeout: 0, batchMaxCount: 20});
provider.pollingInterval = 1000;
function transientKind(e) {
  const code = errorCode(e);
  const text = `${e?.shortMessage || ''} ${e?.message || ''} ${e?.error?.message || ''} ${e?.info?.error?.message || ''}`.toLowerCase();
  if (/already known|known transaction|nonce too low|nonce has already/.test(text)) return 'same-hash-or-nonce-already-known';
  if (/timeout|timed out|429|rate limit|temporar|503|502|504|socket|connection|network|rpc.*unavailable|missing response/.test(text)) return 'transient-rpc-transport';
  if (['NETWORK_ERROR', 'TIMEOUT', 'SERVER_ERROR', 'UNKNOWN_ERROR'].includes(code)) return 'rpc-transient-or-unknown';
  return null;
}
class ReliableWallet extends Wallet {
  async sendTransaction(request) {
    // Populate once and sign once. Every retry broadcasts these identical bytes;
    // retrying never allocates another nonce or signs a replacement operation.
    const populated = await this.populateTransaction(request);
    const signed = await this.signTransaction(populated);
    const transactionHash = keccak256(signed);
    const intent = {...activeIntent, hash: transactionHash, from: this.address, to: populated.to || null,
      nonce: populated.nonce, chainId: Number(populated.chainId), value: populated.value || 0n,
      calldataHash: keccak256(populated.data || '0x')};
    append('prepared-intents.jsonl', intent);
    checkpoint.preparedTransaction = {hash: transactionHash, nonce: populated.nonce, label: activeIntent?.label || null};
    saveCheckpoint();
    for (let attempt = 0; attempt < 5; attempt++) {
      try {
        const response = await provider.broadcastTransaction(signed);
        if (response.hash !== transactionHash) throw Error('Broadcast hash differs from the once-signed transaction');
        return response;
      } catch (e) {
        const kind = transientKind(e);
        let receipt = null, existing = null;
        try {receipt = await provider.getTransactionReceipt(transactionHash); existing = await provider.getTransaction(transactionHash);} catch {}
        if (existing) return existing;
        if (receipt) return {hash: transactionHash, from: this.address, to: populated.to || null,
          nonce: populated.nonce, chainId: populated.chainId, wait: async () => receipt};
        append('broadcast-attempts.jsonl', {hash: transactionHash, nonce: populated.nonce, attempt: attempt + 1,
          errorCode: errorCode(e), classification: kind || 'nontransient',
          rpcErrorCode: typeof e?.info?.error?.code === 'number' ? e.info.error.code : null,
          note: 'Signed bytes remain memory-only; no replacement nonce is allocated.'});
        if (!kind || attempt === 4) throw e;
        await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
      }
    }
    throw Error('Exact transaction retries exhausted');
  }
}
const rootWallet = new ReliableWallet(rootKey, provider);
// NonceManager keeps serial nonces monotonic even when RPC replicas lag a mined
// receipt. Its fully populated request has a fixed nonce and fees before the
// ReliableWallet's final normalization; signing and exact-byte retry occur once.
const root = new NonceManager(rootWallet);
if (rootWallet.address !== EXPECT_ROOT) throw Error('Unexpected funded test wallet');
if ((await provider.getNetwork()).chainId !== 84532n) throw Error('Base Sepolia chain ID required');
for (const actor of personas) {
  const key = keccak256(toUtf8Bytes(`circle-coldstart-v1:${rootKey}:${actor.id}`));
  actor.wallet = new ReliableWallet(key, provider);
  actor.signer = new NonceManager(actor.wallet);
  actor.address = actor.wallet.address;
}
const byId = new Map(personas.map(a => [a.id, a]));
const tokenAbi = ['function balanceOf(address) view returns(uint256)', 'function allowance(address,address) view returns(uint256)',
  'function decimals() view returns(uint8)', 'function approve(address,uint256) returns(bool)', 'function transfer(address,uint256) returns(bool)'];
const token = new Contract(TOKEN, tokenAbi, root);
if (await provider.getCode(TOKEN) === '0x' || await token.decimals() !== 6n) throw Error('Canonical Circle test-token binding failed');
const currentRoot = {USDC: await token.balanceOf(EXPECT_ROOT), ETH: await provider.getBalance(EXPECT_ROOT)};
const rootBefore = priorPacket ? {USDC: BigInt(priorPacket.manifest.rootBefore.USDC), ETH: BigInt(priorPacket.manifest.rootBefore.ETH)} : currentRoot;
if (!priorPacket && (rootBefore.USDC < u('819.8') || rootBefore.ETH < parseEther('0.01'))) throw Error('Insufficient bounded test funding');
if (priorPacket) {
  for (const a of personas) {
    const old = priorPacket.manifest.roster.find(x => x.id === a.id);
    if (!old || old.address !== a.address || old.role !== a.role) throw Error('Resume role identities differ from the funded actors');
  }
  write('prior-manifest.json', priorPacket.manifest);
  write('prior-deployment.json', priorPacket.deployment);
} else {
  for (const a of [...clients, ...backers, ...sponsors]) {
    if (await provider.getTransactionCount(a.address) !== 0 || await token.balanceOf(a.address) !== 0n) {
      throw Error('Derived role wallet has prior execution state; do not overwrite funded actors');
    }
  }
}
write('manifest.json', {...manifest, rootAddress: EXPECT_ROOT, rootBefore,
  ...(priorPacket ? {resume: {bootstrapOnly: true, priorRunnerSha256: priorPacket.manifest.runnerSha256,
    priorManifestSha256: sha(fs.readFileSync(path.join(resumePath, 'manifest.json')))}} : {}),
  roster: personas.map(({wallet, signer, ...a}) => a).concat([
    {id: 'issuer-01', role: 'issuer', address: EXPECT_ROOT}, {id: 'adjudicator-01', role: 'adjudicator', address: EXPECT_ROOT},
  ])});
saveCheckpoint();

async function send(label, actor, call, args, operation) {
  if (confirmedLabels.has(label)) {
    const old = confirmedLabels.get(label);
    const expected = serial(args), keys = Object.keys(expected).sort(), oldKeys = Object.keys(old.args).sort();
    if (old.call !== call || old.from !== actor.address || keys.join('|') !== oldKeys.join('|')
      || keys.some(key => String(expected[key]).toLowerCase() !== String(old.args[key]).toLowerCase())) {
      throw Error('Confirmed bootstrap label has a different action, signer or safe parameters');
    }
    append('resume-skips.jsonl', {label, hash: old.hash, call, reason: 'Prior exact call and mined receipt independently verified'});
    return provider.getTransactionReceipt(old.hash);
  }
  if (rootFees >= parseEther('0.03')) throw Error('Root gas-use limit reached');
  activeIntent = {label, actor: actor.id || 'operator', call, args: serial(args)};
  let tx;
  try {tx = await operation();} finally {activeIntent = null;}
  const item = {label, actor: actor.id || 'operator', from: tx.from, to: tx.to,
    call, args: serial(args), hash: tx.hash, nonce: tx.nonce, chainId: Number(tx.chainId), status: 'broadcast'};
  journal.push(item); write('transactions.json', journal);
  console.log(`TX ${journal.length} ${label} ${tx.hash}`);
  const receipt = await freshRead(() => tx.wait(1));
  if (!receipt || receipt.hash !== tx.hash || receipt.status !== 1) throw Error('Transaction did not succeed');
  lastMinedBlock = receipt.blockNumber;
  const fee = receipt.fee;
  allFees += fee;
  if (tx.from.toLowerCase() === EXPECT_ROOT.toLowerCase()) rootFees += fee;
  Object.assign(item, {blockNumber: receipt.blockNumber, status: receipt.status,
    gasUsed: receipt.gasUsed.toString(), feeWei: fee.toString(),
    events: receipt.logs.map(log => {
      try {
        const e = iface.parseLog(log);
        if (!e) return null;
        return {name: e.name, args: serial(e.args.toObject())};
      } catch { return null; }
    }).filter(Boolean)});
  if (gt) {
    const tag = {blockTag: receipt.blockNumber};
    const [reserve, stake, dues, sponsorCapital, tokenBalance] = await freshRead(() => Promise.all([
      gt.reserve(tag), gt.totalStake(tag), gt.totalDues(tag), gt.sponsorCapital(tag), token.balanceOf(gt.target, tag),
    ]));
    item.ledgerAfter = serial({reserve, stake, dues, sponsorCapital, tokenBalance,
      tokenEqualsReservePlusStake: tokenBalance === reserve + stake,
      reserveEqualsSponsorCapitalPlusDues: reserve === sponsorCapital + dues});
    if (tokenBalance !== reserve + stake || reserve !== sponsorCapital + dues) throw Error('Transition ledger identity failed');
  }
  write('transactions.json', journal);
  checkpoint.lastTransactionHash = tx.hash;
  delete checkpoint.preparedTransaction;
  saveCheckpoint();
  if (REHEARSAL && process.env.REHEARSAL_STOP_AFTER_LABEL === label) {
    throw Error('Requested localhost rehearsal stop after a persisted receipt');
  }
  return receipt;
}
const rootActor = {id: 'operator', address: EXPECT_ROOT};
async function gasFor(actor) {
  const amount = parseEther('0.00008');
  if (confirmedLabels.has(`gas-${actor.id}`)) {
    await send(`gas-${actor.id}`, rootActor, 'native ETH transfer', {to: actor.address, value: amount},
      () => root.sendTransaction({to: actor.address, value: amount}));
    return;
  }
  if (gasFunded + amount > parseEther('0.005')) throw Error('Role gas-funding limit reached');
  gasFunded += amount;
  await send(`gas-${actor.id}`, rootActor, 'native ETH transfer', {to: actor.address, value: amount},
    () => root.sendTransaction({to: actor.address, value: amount}));
}
async function fund(actor, amount) {
  await send(`tokens-${actor.id}`, rootActor, 'USDC.transfer', {to: actor.address, amount},
    () => token.transfer(actor.address, amount));
}
const tokenFor = a => token.connect(a.signer);
const factory = new ContractFactory(artifact.abi, bytecode, root);
let gt;
if (process.env.COLDSTART_GT || priorPacket) {
  const priorAddress = priorPacket?.checkpoint.contract;
  if (priorAddress && process.env.COLDSTART_GT && getAddress(process.env.COLDSTART_GT) !== priorAddress) {
    throw Error('Bootstrap resume would replace the funded contract');
  }
  gt = new Contract(getAddress(process.env.COLDSTART_GT || priorAddress), artifact.abi, root);
  if (await gt.guaranteeCount() !== 0n || await gt.outstanding() !== 0n || await gt.totalDues() !== 0n || await gt.issuerSpent() !== 0n) {
    throw Error('Bootstrap resume has market exposure or consumed capacity');
  }
  if (!priorPacket && (await gt.reserve() !== 0n || await gt.totalStake() !== 0n)) {
    throw Error('Provided deployment is not an unused cold-start contract');
  }
  const priorHash = priorPacket?.deployment.hash || process.env.COLDSTART_DEPLOYMENT_HASH;
  if (!priorHash) throw Error('Prior deployment receipt required for explicit resume');
  const prior = await provider.getTransactionReceipt(priorHash);
  if (!prior || prior.status !== 1 || prior.contractAddress !== gt.target || prior.from !== EXPECT_ROOT) {
    throw Error('Prior deployment receipt does not match the unused contract');
  }
  lastMinedBlock = priorPacket ? Math.max(prior.blockNumber, ...journal.map(x => x.blockNumber)) : prior.blockNumber;
  write('prior-deployment.json', {hash: prior.hash, contract: prior.contractAddress, blockNumber: prior.blockNumber,
    status: prior.status, from: prior.from, gasUsed: prior.gasUsed.toString(), feeWei: prior.fee.toString(),
    note: 'Confirmed creation from the earlier stopped preflight; no new deployment transaction.'});
} else {
  const deployTx = await factory.getDeployTransaction(TOKEN, EXPECT_ROOT, EXPECT_ROOT, EXPECT_ROOT, u('6'), U);
  const r = await send('deploy-GuaranteeTrust-r6-Circle', rootActor, 'constructor',
    {token: TOKEN, owner: EXPECT_ROOT, adjudicator: EXPECT_ROOT, issuer: EXPECT_ROOT, issuerBudget: u('6'), unit: U},
    () => root.sendTransaction(deployTx));
  gt = new Contract(r.contractAddress, artifact.abi, root);
}
const GT = await gt.getAddress();
checkpoint.contract = GT; checkpoint.token = TOKEN; checkpoint.phase = 'deployed'; saveCheckpoint();
const code = await freshRead(async () => {
  const value = await provider.getCode(GT, lastMinedBlock);
  if (value === '0x') throw Error('Confirmed deployment code not yet available from RPC');
  return value;
});
function maskRuntime(hex) {
  const bytes = Uint8Array.from(Buffer.from(hex.slice(2), 'hex'));
  for (const refs of Object.values(artifact.immutableReferences || artifact.deployedBytecode.immutableReferences || {})) {
    for (const {start, length} of refs) bytes.fill(0, start, start + length);
  }
  return `0x${Buffer.from(bytes).toString('hex')}`;
}
const deploymentTag = {blockTag: lastMinedBlock};
const boundRoles = await freshRead(() => Promise.all([gt.token(deploymentTag), gt.owner(deploymentTag), gt.adjudicator(deploymentTag), gt.issuer(deploymentTag)]));
write('runtime-check.json', {blockNumber: lastMinedBlock, expectedMaskedHash: keccak256(maskRuntime(runtime)),
  actualMaskedHash: keccak256(maskRuntime(code)), runtimeBytes: (code.length - 2) / 2, token: boundRoles[0],
  owner: boundRoles[1], adjudicator: boundRoles[2], issuer: boundRoles[3]});
if (maskRuntime(code) !== maskRuntime(runtime) || boundRoles[0] !== TOKEN || boundRoles[1] !== EXPECT_ROOT
  || boundRoles[2] !== EXPECT_ROOT || boundRoles[3] !== EXPECT_ROOT) {
  throw Error('Reviewed runtime/token/role binding failed');
}
const domain = {name: 'GuaranteeTrust', version: '2', chainId: 84532, verifyingContract: GT};
const immutableRefs = artifact.immutableReferences || artifact.deployedBytecode.immutableReferences || {};
const expectedImmutables = {
  '56710': zeroPadValue(TOKEN, 32),
  '1424': zeroPadValue(toBeHex(84532), 32),
  '1426': zeroPadValue(GT, 32),
  '1428': keccak256(toUtf8Bytes('GuaranteeTrust')),
  '1430': keccak256(toUtf8Bytes('2')),
  '1422': TypedDataEncoder.hashDomain(domain),
  '1433': toBeHex(BigInt(zeroPadBytes(hexlify(toUtf8Bytes('GuaranteeTrust')), 32)) | BigInt(toUtf8Bytes('GuaranteeTrust').length), 32),
  '1436': toBeHex(BigInt(zeroPadBytes(hexlify(toUtf8Bytes('2')), 32)) | 1n, 32),
};
if (Object.keys(immutableRefs).some(id => !(id in expectedImmutables))) throw Error('Unexpected reviewed runtime immutable');
for (const [id, expected] of Object.entries(expectedImmutables)) {
  const refs = immutableRefs[id];
  if (!refs?.length || (id === '56710' && refs.length !== 7)) throw Error('Reviewed immutable references missing');
  for (const {start, length} of refs) {
    const actual = `0x${code.slice(2 + start * 2, 2 + (start + length) * 2)}`;
    if (length !== 32 || actual.toLowerCase() !== expected.toLowerCase()) throw Error('Constructor immutable binding failed');
  }
}
write('deployment.json', {sourceCommit: SOURCE, contract: GT, token: TOKEN,
  deploymentHash: journal.find(x => x.call === 'constructor')?.hash || priorPacket?.deployment.hash || process.env.COLDSTART_DEPLOYMENT_HASH || null,
  runtimeHash: keccak256(code), maskedRuntimeHash: keccak256(maskRuntime(code)), artifactSha256: sha(artifactBytes),
  owner: EXPECT_ROOT, issuer: EXPECT_ROOT, adjudicator: EXPECT_ROOT, chainId: 84532, rehearsal: REHEARSAL,
  verifiedImmutableValues: expectedImmutables});
if (priorPacket) {
  const allowedCalls = new Set(['constructor', 'setParams', 'native ETH transfer', 'USDC.transfer', 'USDC.approve',
    'fundReserve', 'stake', 'setConsentBySig', 'attest', 'setLine']);
  const expectedInputs = record => {
    const a = record.args;
    switch (record.call) {
      case 'USDC.transfer': return [a.to, a.amount];
      case 'USDC.approve': return [a.spender, a.amount];
      case 'fundReserve': case 'stake': return [a.amount];
      case 'attest': case 'setLine': return [a.worker, a.amount];
      case 'setConsentBySig': return [a.member, a.attester, a.allowed, a.nonce, a.deadline];
      case 'setParams': return [a.maxShareBps, a.floorMultiple, a.contributionBps, a.contributionCap,
        a.remitWindow, a.lineCap, a.attestCap, a.maxAttesters, a.maxOpenAttestees];
      default: return null;
    }
  };
  for (const record of journal) {
    if (!allowedCalls.has(record.call) || record.status !== 1 || confirmedLabels.has(record.label)) {
      throw Error('Resume journal contains a duplicate, unconfirmed or nonbootstrap action');
    }
    const actor = record.actor === 'operator' ? rootActor : byId.get(record.actor);
    if (!actor || actor.address !== record.from) throw Error('Resume journal signer is not the declared role');
    const [tx, receipt] = await freshRead(() => Promise.all([
      provider.getTransaction(record.hash), provider.getTransactionReceipt(record.hash),
    ]));
    if (!tx || !receipt || receipt.status !== 1 || receipt.hash !== record.hash || tx.from !== record.from
      || tx.to !== record.to || tx.nonce !== record.nonce || tx.chainId !== 84532n || receipt.blockNumber !== record.blockNumber) {
      throw Error('Prior bootstrap transaction does not match its actual mined receipt');
    }
    if (record.call === 'native ETH transfer') {
      if (tx.to !== record.args.to || tx.value !== BigInt(record.args.value) || tx.data !== '0x') {
        throw Error('Prior native gas-funding call differs from the recorded intent');
      }
      gasFunded += tx.value;
    } else if (record.call === 'constructor') {
      const expectedCreation = bytecode + iface.encodeDeploy([TOKEN, EXPECT_ROOT, EXPECT_ROOT, EXPECT_ROOT, u('6'), U]).slice(2);
      if (tx.to !== null || receipt.contractAddress !== GT || tx.data !== expectedCreation) {
        throw Error('Prior creation transaction differs from the reviewed deployment');
      }
    } else {
      const isToken = record.call.startsWith('USDC.');
      if (tx.to !== (isToken ? TOKEN : GT)) throw Error('Prior bootstrap call targets a different token or contract');
      const decoded = (isToken ? token.interface : iface).parseTransaction({data: tx.data, value: tx.value});
      const expectedName = isToken ? record.call.slice(5) : record.call;
      const expected = expectedInputs(record);
      if (!decoded || decoded.name !== expectedName || !expected
        || expected.some((value, i) => String(value).toLowerCase() !== String(decoded.args[i]).toLowerCase())) {
        throw Error('Prior bootstrap calldata differs from its safe recorded parameters');
      }
    }
    const fee = receipt.fee;
    if (BigInt(record.feeWei) !== fee || BigInt(record.gasUsed) !== receipt.gasUsed) throw Error('Prior receipt gas accounting differs');
    allFees += fee; if (tx.from === EXPECT_ROOT) rootFees += fee;
    lastMinedBlock = Math.max(lastMinedBlock, receipt.blockNumber);
    confirmedLabels.set(record.label, record);
  }
  if (gasFunded > parseEther('0.005') || rootFees >= parseEther('0.03')) throw Error('Resumed bootstrap already exceeds its resource caps');
  const [rootLatestNonce, rootPendingNonce] = await Promise.all([
    provider.getTransactionCount(EXPECT_ROOT, 'latest'), provider.getTransactionCount(EXPECT_ROOT, 'pending'),
  ]);
  const expectedRootNonce = 1 + Math.max(...journal.filter(x => x.from === EXPECT_ROOT).map(x => x.nonce));
  if (rootLatestNonce !== expectedRootNonce || rootPendingNonce !== rootLatestNonce) {
    throw Error('Unrecorded mined or pending root transaction requires reconciliation before resuming');
  }
  // Reconcile current assets with the confirmed bootstrap, including recovered
  // lost-response transactions. A matching wallet balance alone is insufficient.
  const expectedBalances = new Map(personas.map(a => [a.address, 0n]));
  const expectedStakes = new Map(backers.map(a => [a.address, 0n]));
  const expectedLines = new Map(workers.map(a => [a.address, 0n]));
  let expectedReserve = 0n, expectedStake = 0n;
  for (const r of journal) {
    if (r.call === 'USDC.transfer') expectedBalances.set(r.args.to, expectedBalances.get(r.args.to) + BigInt(r.args.amount));
    if (r.call === 'fundReserve' || r.call === 'stake') {
      const amount = BigInt(r.args.amount);
      expectedBalances.set(r.from, expectedBalances.get(r.from) - amount);
      if (r.call === 'fundReserve') expectedReserve += amount;
      else {expectedStake += amount; expectedStakes.set(r.from, expectedStakes.get(r.from) + amount);}
    }
    if (r.call === 'setLine') expectedLines.set(r.args.worker, BigInt(r.args.amount));
  }
  for (const actor of personas) {
    const actual = await freshRead(() => token.balanceOf(actor.address));
    if (actual !== expectedBalances.get(actor.address)) throw Error('Role token balance differs from the confirmed bootstrap; do not fund again');
  }
  for (const actor of [...workers, ...backers]) {
    const member = await freshRead(() => gt.memberOf(actor.address));
    if (member.stake !== (expectedStakes.get(actor.address) || 0n) || member.line !== (expectedLines.get(actor.address) || 0n)
      || member.dues !== 0n || member.committedLine !== 0n || member.committedDues !== 0n || member.backingCommitted !== 0n) {
      throw Error('Role capacity or exposure differs from the confirmed bootstrap');
    }
  }
  for (const backer of backers) for (const id of backer.workers) {
    const worker = byId.get(id);
    const consentRecord = confirmedLabels.get(`consent-${id}-${backer.id}`);
    const attestRecord = confirmedLabels.get(`attest-${backer.id}-${id}`);
    if (await gt.consent(worker.address, backer.address) !== Boolean(consentRecord)
      || await gt.consentNonce(worker.address, backer.address) !== (consentRecord ? BigInt(consentRecord.args.nonce) + 1n : 0n)
      || await gt.backing(backer.address, worker.address) !== (attestRecord ? BigInt(attestRecord.args.amount) : 0n)) {
      throw Error('Backing or consent differs from the confirmed bootstrap');
    }
  }
  const [reserve, stake, dues, sponsorCapital, balance] = await Promise.all([
    gt.reserve(), gt.totalStake(), gt.totalDues(), gt.sponsorCapital(), token.balanceOf(GT),
  ]);
  if (reserve !== expectedReserve || stake !== expectedStake || dues !== 0n || sponsorCapital !== reserve
    || balance !== reserve + stake || await gt.guaranteeCount() !== 0n || await gt.outstanding() !== 0n) {
    throw Error('Funded contract state differs from the confirmed bootstrap');
  }
  const remainingTokenFunding = u('819.8') - journal.filter(r => r.call === 'USDC.transfer').reduce((n, r) => n + BigInt(r.args.amount), 0n);
  if (currentRoot.USDC < remainingTokenFunding) throw Error('Remaining root tokens cannot complete the original bounded funding');
  fs.copyFileSync(path.join(resumePath, 'transactions.json'), path.join(out, 'prior-transactions.json'));
  write('resume-verification.json', {verifiedAtUTC: new Date().toISOString(), contract: GT,
    originalJournalCount: priorPacket.journal.length, recoveredTransactions: priorPacket.recovery?.additionalConfirmedTransactions || [],
    verifiedTransactions: journal.length, lastMinedBlock, rootLatestNonce, rootPendingNonce, gasFunded, rootFees, allFees,
    reserve, stake, dues, sponsorCapital, tokenBalance: balance, remainingTokenFunding,
    policyUnchanged: true, guaranteeCount: 0, outstanding: 0});
  write('transactions.json', journal);
}
await send('configure-small-test-caps', rootActor, 'setParams',
  {maxShareBps: 2000, floorMultiple: 2, contributionBps: 500, contributionCap: u('0.3'), remitWindow: 86400,
    lineCap: u('2'), attestCap: u('2'), maxAttesters: 5, maxOpenAttestees: 5},
  () => gt.setParams(2000, 2, 500, u('0.3'), 86400, u('2'), u('2'), 5, 5));
const block = await provider.getBlock('latest');
const settleBy = block.timestamp + 7 * 86400;
const holdUntil = block.timestamp + 14 * 86400;
function acceptance(worker, client, amount, termsHash) {
  return {worker: worker.address, clientId: client.clientId, groupId: client.groupId, amount,
    maxFromDues: amount, termsHash, contributionBps: 500n, contributionCap: u('0.3'), remitWindow: 86400n,
    settleBy, holdUntil, nonce: nextNonce++, deadline: block.timestamp + 2 * 86400};
}
const zero = acceptance(workers[0], clients[0], u('0.2'), hash({kind: 'zero-reserve-control'}));
if (priorPacket) {
  if (priorPacket.zero.expected !== 'ExposureCap' || priorPacket.zero.actual !== 'ExposureCap'
    || priorPacket.zero.reserve !== '0' || priorPacket.zero.guaranteeAmount !== '200000' || priorPacket.zero.accepted !== false) {
    throw Error('Prior zero-reserve control proof is inconsistent');
  }
  fs.copyFileSync(path.join(resumePath, 'zero-reserve-control.json'), path.join(out, 'zero-reserve-control.json'));
} else {
  const zeroSig = await workers[0].wallet.signTypedData(domain, acceptanceTypes, zero);
  let zeroError = null;
  try {await gt.openGuarantee.staticCall(zero, zeroSig, {blockTag: lastMinedBlock});} catch (e) {
    try {zeroError = iface.parseError(e.data || e.info?.error?.data)?.name;} catch {}
    zeroError ||= errorCode(e);
  }
  if (zeroError !== 'ExposureCap') throw Error('Zero-reserve negative control did not reject at ExposureCap');
  write('zero-reserve-control.json', {method: 'eth_call; no transaction and no state change', expected: 'ExposureCap', actual: zeroError,
    reserve: await gt.reserve(), guaranteeAmount: u('0.2'), accepted: false});
}
for (const sponsor of sponsors) {
  await gasFor(sponsor); await fund(sponsor, u('0.75'));
  await send(`approve-${sponsor.id}`, sponsor, 'USDC.approve', {spender: GT, amount: u('0.75')},
    () => tokenFor(sponsor).approve(GT, u('0.75')));
  await send(`seed-${sponsor.id}`, sponsor, 'fundReserve', {amount: u('0.5')},
    () => gt.connect(sponsor.signer).fundReserve(u('0.5')));
}
for (const backer of backers) {
  await gasFor(backer); await fund(backer, u('1.2'));
  await send(`approve-${backer.id}`, backer, 'USDC.approve', {spender: GT, amount: u('1.2')},
    () => tokenFor(backer).approve(GT, u('1.2')));
  await send(`stake-initial-${backer.id}`, backer, 'stake', {amount: u('0.3')},
    () => gt.connect(backer.signer).stake(u('0.3')));
  for (const id of backer.workers) {
    const worker = byId.get(id);
    const oldConsent = confirmedLabels.get(`consent-${worker.id}-${backer.id}`);
    if (oldConsent) {
      await send(oldConsent.label, rootActor, 'setConsentBySig', oldConsent.args,
        () => {throw Error('Confirmed consent must never be broadcast again');});
      await send(`attest-${backer.id}-${worker.id}`, backer, 'attest', {worker: worker.address, amount: u('0.15')},
        () => gt.connect(backer.signer).attest(worker.address, u('0.15')));
      continue;
    }
    const nonce = await gt.consentNonce(worker.address, backer.address);
    const consent = {member: worker.address, attester: backer.address, allowed: true, nonce, deadline: zero.deadline};
    const signature = await worker.wallet.signTypedData(domain, consentTypes, consent);
    await send(`consent-${worker.id}-${backer.id}`, rootActor, 'setConsentBySig', consent,
      () => gt.setConsentBySig(worker.address, backer.address, true, nonce, zero.deadline, signature));
    await send(`attest-${backer.id}-${worker.id}`, backer, 'attest', {worker: worker.address, amount: u('0.15')},
      () => gt.connect(backer.signer).attest(worker.address, u('0.15')));
  }
}
for (const worker of workers.slice(0, 8)) {
  await send(`line-${worker.id}`, rootActor, 'setLine', {worker: worker.address, amount: u('0.2')},
    () => gt.setLine(worker.address, u('0.2')));
}
for (const client of clients) {await gasFor(client); await fund(client, u('20'));}
checkpoint.phase = 'funded'; saveCheckpoint();
async function snapshot(round) {
  const tag = {blockTag: lastMinedBlock};
  const [reserve, outstanding, stake, dues, sponsorCapital, issuerHeld, issuerSpent, balance, guaranteeCount, latest] = await freshRead(() => Promise.all([
    gt.reserve(tag), gt.outstanding(tag), gt.totalStake(tag), gt.totalDues(tag), gt.sponsorCapital(tag), gt.issuerHeld(tag), gt.issuerSpent(tag),
    token.balanceOf(GT, tag), gt.guaranteeCount(tag), provider.getBlock(lastMinedBlock),
  ]));
  const s = {round, blockNumber: latest.number, timestamp: latest.timestamp, reserve, outstanding, stake, dues,
    sponsorCapital, issuerHeld, issuerSpent, tokenBalance: balance, guaranteeCount,
    identities: {tokenEqualsReservePlusStake: balance === reserve + stake,
      reserveEqualsSponsorCapitalPlusDues: reserve === sponsorCapital + dues}};
  if (!Object.values(s.identities).every(Boolean)) throw Error('Accounting identity failed');
  return s;
}
const initial = await snapshot(0); write('initial-state.json', initial);
const refuse = (round, client, worker, reason, amount) => {
  counts.refusals[reason] = (counts.refusals[reason] || 0) + 1;
  append('policy-events.jsonl', {kind: 'refused', round, client: client.id, worker: worker.id, reason, amount,
    evidence: 'Contract-state precheck; no broadcast and no refusal event onchain'});
};
for (let round = 1; round <= ROUNDS; round++) {
  checkpoint.phase = 'round'; checkpoint.round = round; saveCheckpoint();
  const before = await snapshot(round - 1);
  const start = {opened: counts.opened, paid: counts.paid, claimed: counts.claimed, cancelled: counts.cancelled,
    wages: counts.wages, contributions: counts.contributions, claims: counts.claims, topups: sponsorTopups,
    reserveRefusals: ['ExposureCap', 'GroupCap', 'ReserveFloor'].reduce((n, r) => n + (counts.refusals[r] || 0), 0)};
  const prior = rounds.at(-1);
  if (round <= 12 && prior && prior.paid >= 3) {
    for (const backer of backers) {
      if (backer.laterStake >= u('0.9') || rng() >= 0.18) continue;
      const amount = u('0.1');
      await send(`stake-round-${round}-${backer.id}`, backer, 'stake', {amount},
        () => gt.connect(backer.signer).stake(amount));
      backer.laterStake += amount; counts.laterStake += amount;
      for (const id of backer.workers) {
        const worker = byId.get(id);
        await send(`attest-round-${round}-${backer.id}-${id}`, backer, 'attest', {worker: worker.address, amount: u('0.05')},
          () => gt.connect(backer.signer).attest(worker.address, u('0.05')));
      }
    }
  }
  if (round <= 12 && prior && prior.paid >= 4 * prior.claimed && prior.paid >= 3
    && sponsorTopups < u('1') && (before.reserve < u('2.8') || prior.reserveRefusals > 0)) {
    const sponsor = sponsors.find(s => s.added === 0n);
    if (sponsor) {
      await send(`topup-round-${round}-${sponsor.id}`, sponsor, 'fundReserve', {amount: u('0.25'),
        policyReason: 'Observed settled work, low claim pressure and reserve pressure'},
        () => gt.connect(sponsor.signer).fundReserve(u('0.25')));
      sponsor.added = u('0.25'); sponsorTopups += u('0.25');
    }
  }
  for (const client of clients) {
    if (rng() >= client.postProbability) continue;
    counts.posted++;
    const worker = workers[Math.floor(rng() * workers.length)];
    const wage = BigInt(client.wageLowTenths + Math.floor(rng() * (client.wageHighTenths - client.wageLowTenths + 1))) * 100000n;
    let amount = wage / 10n;
    if (amount < u('0.2')) amount = u('0.2'); if (amount > u('0.8')) amount = u('0.8');
    const [reserve, outstanding, groupExposure, clientOpen, clientDefaulted, groupDefaulted, capacity, member] = await Promise.all([
      gt.reserve(), gt.outstanding(), gt.groupExposure(client.groupId), gt.clientOpen(client.clientId),
      gt.clientDefaulted(client.clientId), gt.groupDefaulted(client.groupId), gt.capacity(worker.address), gt.memberOf(worker.address),
    ]);
    let reason;
    if (clientOpen || clientDefaulted || groupDefaulted) reason = 'ClientBlocked';
    else if (member.unpaidContributions !== 0n) reason = 'ContributionOutstanding';
    else if (amount * 10000n > reserve * 2000n) reason = 'ExposureCap';
    else if ((groupExposure + amount) * 10000n > reserve * 3000n) reason = 'GroupCap';
    else if (outstanding + 3n * amount > reserve) reason = 'ReserveFloor';
    else if (capacity < amount) reason = 'InsufficientCapacity';
    if (reason) {refuse(round, client, worker, reason, amount); continue;}
    const qualityPassed = rng() < worker.qualityProbability;
    const clientPaysDraw = rng() < client.payProbability;
    const paid = qualityPassed && clientPaysDraw;
    if (paid && await token.balanceOf(client.address) < wage) {
      refuse(round, client, worker, 'ClientPrefundingExhausted', amount); continue;
    }
    const contributionDue = wage * 500n / 10000n > u('0.3') ? u('0.3') : wage * 500n / 10000n;
    const netWage = wage - contributionDue;
    const terms = {schema: 'synthetic-first-job/1', round, client: client.id, worker: worker.id,
      wage: wage.toString(), guarantee: amount.toString(), contributionBps: 500, contributionCap: '300000',
      maxFromDues: amount.toString(), synthetic: true,
      paymentAuthorization: 'Client transfers gross wage minus contribution, then remits the withheld amount for the worker',
      netWage: netWage.toString(), withheldContribution: contributionDue.toString()};
    const signed = acceptance(worker, client, amount, hash(terms));
    const signature = await worker.wallet.signTypedData(domain, acceptanceTypes, signed);
    // Validate exact live acceptance before broadcasting; a static refusal is recorded honestly.
    let id;
    try {id = await gt.openGuarantee.staticCall(signed, signature, {blockTag: lastMinedBlock});} catch (e) {
      let name; try {name = iface.parseError(e.data || e.info?.error?.data)?.name;} catch {}
      if (!name) throw e;
      refuse(round, client, worker, name, amount); continue;
    }
    await send(`open-round-${round}-g${id}`, rootActor, 'openGuarantee', {id, acceptance: signed},
      () => gt.openGuarantee(signed, signature));
    counts.opened++;
    append('policy-events.jsonl', {kind: 'opened', round, id, terms, acceptance: signed,
      draws: {qualityPassed, clientPaysDraw},
      outcome: !qualityPassed ? 'synthetic-cancelled-nondelivery' : paid ? 'synthetic-paid' : 'synthetic-nonpayment'});
    if (!qualityPassed) {
      const reasonHash = hash({synthetic: true, guarantee: id.toString(), reason: 'Work not delivered; parties agree to cancellation'});
      const resolutionHash = hash({synthetic: true, guarantee: id.toString(), resolution: 'Mutually resolved nondelivery; no client wage obligation and no guarantee claim'});
      if (counts.cancelled === 0) {
        await send(`dispute-nondelivery-g${id}`, rootActor, 'openDispute', {id, reasonHash, synthetic: true},
          () => gt.openDispute(id, reasonHash));
      }
      await send(`cancel-nondelivery-g${id}`, rootActor, 'cancelGuarantee', {id, resolutionHash, synthetic: true},
        () => gt.cancelGuarantee(id, resolutionHash));
      counts.cancelled++;
    } else if (paid) {
      const wageReceipt = await send(`wage-g${id}-${client.id}-${worker.id}`, client, 'USDC.transfer',
        {worker: worker.address, grossWage: wage, netWage, withheldContribution: contributionDue, synthetic: true},
        () => tokenFor(client).transfer(worker.address, netWage));
      const evidenceHash = hash({synthetic: true, guarantee: id.toString(), wageTransaction: wageReceipt.hash,
        outcome: 'paid', termsHash: signed.termsHash});
      await send(`paid-g${id}`, rootActor, 'markPaid', {id, wage, evidenceHash},
        () => gt.markPaid(id, wage, evidenceHash));
      const g = await gt.guarantee(id);
      if (g.contributionDue !== contributionDue) throw Error('Signed withholding differs from contract due');
      // The client's transfer and remittance together equal the signed gross wage.
      // remit() permits a third-party payer, preserving worker gaslessness.
      const payer = client;
      if (await token.allowance(payer.address, GT) < g.contributionDue) {
        await send(`approve-contributions-${payer.id}`, payer, 'USDC.approve', {spender: GT, amount: u('20')},
          () => tokenFor(payer).approve(GT, u('20')));
      }
      await send(`remit-g${id}`, payer, 'remit', {id, contributionDue: g.contributionDue,
        payerNote: 'Client remits the contribution withheld from the signed gross wage; its total outflow equals gross wage'},
        () => gt.connect(payer.signer).remit(id));
      counts.paid++; counts.remitted++; counts.wages += wage; counts.netWages += netWage; counts.contributions += g.contributionDue;
    } else {
      const evidenceHash = hash({synthetic: true, guarantee: id.toString(), outcome: 'simulated-client-nonpayment',
        qualityPassed, clientPaysDraw, termsHash: signed.termsHash});
      await send(`claim-g${id}`, rootActor, 'claim', {id, evidenceHash, synthetic: true},
        () => gt.claim(id, evidenceHash));
      counts.claimed++; counts.claims += amount;
    }
    await snapshot(round);
  }
  const after = await snapshot(round);
  const row = {...after, reserveBefore: before.reserve,
    opened: counts.opened - start.opened, paid: counts.paid - start.paid, claimed: counts.claimed - start.claimed,
    cancelled: counts.cancelled - start.cancelled,
    wages: counts.wages - start.wages, contributions: counts.contributions - start.contributions,
    claims: counts.claims - start.claims, sponsorTopups: sponsorTopups - start.topups,
    reserveRefusals: ['ExposureCap', 'GroupCap', 'ReserveFloor'].reduce((n, r) => n + (counts.refusals[r] || 0), 0) - start.reserveRefusals};
  rounds.push(row); append('round-snapshots.jsonl', row); write('rounds.json', rounds);
  console.log(`ROUND ${round} ${JSON.stringify(serial({opened: row.opened, paid: row.paid, claimed: row.claimed,
    reserveUSDC: formatUnits(row.reserve, 6), reserveRefusals: row.reserveRefusals, sponsorTopupsUSDC: formatUnits(row.sponsorTopups, 6)}))}`);
}
checkpoint.phase = 'shutdown'; saveCheckpoint();
await send('shutdown-pause-origination', rootActor, 'setPaused', {paused: true}, () => gt.setPaused(true));
const terminal = await snapshot(ROUNDS);
const guarantees = [];
for (let id = 0n; id < terminal.guaranteeCount; id++) {
  const g = await gt.guarantee(id);
  if (g.state === 1n) throw Error('Open exposure remains at shutdown');
  guarantees.push({id, worker: g.worker, clientId: g.clientId, groupId: g.groupId, state: Number(g.state),
    amount: g.amount, fromBacking: g.fromBacking, fromLine: g.fromLine, fromDues: g.fromDues,
    wage: g.wage, contributionDue: g.contributionDue, remitted: g.remitted, evidenceHash: g.evidenceHash});
}
const members = [];
for (const actor of [...workers, ...backers]) {
  const m = await gt.memberOf(actor.address);
  if (m.backingCommitted !== 0n || m.committedLine !== 0n || m.committedDues !== 0n || m.unpaidContributions !== 0n) {
    throw Error('A member retains an exposure lock or unpaid contribution');
  }
  members.push({id: actor.id, address: actor.address, ...serial(m.toObject())});
}
if (terminal.outstanding !== 0n || !await gt.paused()) throw Error('Shutdown invariant failed');
const lastSix = rounds.slice(-6);
const gate = {
  windowRounds: [19, 24], sponsorTopups: lastSix.reduce((n, r) => n + r.sponsorTopups, 0n),
  opened: lastSix.reduce((n, r) => n + r.opened, 0),
  throughputEachRound: lastSix.every(r => r.opened > 0),
  reserveChange: lastSix.at(-1).reserve - lastSix[0].reserveBefore,
  reserveRefusals: lastSix.reduce((n, r) => n + r.reserveRefusals, 0),
  identitiesAllRounds: rounds.every(r => Object.values(r.identities).every(Boolean)),
};
gate.success = gate.sponsorTopups === 0n && gate.throughputEachRound && gate.reserveChange >= 0n
  && gate.reserveRefusals === 0 && gate.identitiesAllRounds;
const roleBalances = [];
for (const actor of personas) roleBalances.push({id: actor.id, address: actor.address,
  USDC: await token.balanceOf(actor.address), ETH: await provider.getBalance(actor.address)});
const rootAfter = {USDC: await token.balanceOf(EXPECT_ROOT), ETH: await provider.getBalance(EXPECT_ROOT)};
const actualRootGasCost = rootBefore.ETH - rootAfter.ETH - gasFunded;
const summary = {sourceCommit: SOURCE, contract: GT, token: TOKEN, chainId: 84532, startedAtUTC: checkpoint.startedAtUTC,
  completedAtUTC: new Date().toISOString(), policySeed: SEED, roles: manifest.roles,
  independentAgents: 0, policyCharacters: 100, rounds: ROUNDS, counts, sponsorTopups, gate,
  initial, terminal, sponsorSeed: u('2'), initialBackerStake: u('4.2'), clientPrefunding: u('800'),
  rootBefore, rootAfter, fees: {rootFeeWei: rootFees, allRecordedTransactionFeeWei: allFees, gasFundedWei: gasFunded,
    rootFeeETH: formatEther(rootFees), allRecordedTransactionFeeETH: formatEther(allFees),
    rootETHReconciledGasCostWei: actualRootGasCost, rootETHReconciledGasCost: formatEther(actualRootGasCost),
    note: 'Receipt fee totals are execution fees; root balance reconciliation also captures any Base L1 data fees.'},
  shutdown: {paused: true, openGuarantees: 0, locksReleased: true, sponsorRecoveryAttempted: false,
    retainedReserve: terminal.reserve, retainedStake: terminal.stake, retainedDues: terminal.dues,
    note: 'All retained amounts are test USDC; no function withdraws worker dues. Wallet balances are listed separately.'},
  humanEarnings: 0, humanBenefit: 0, rehearsal: REHEARSAL, caveats: manifest.caveats};
write('guarantees.json', guarantees); write('members.json', members); write('role-balances.json', roleBalances);
write('terminal-state.json', terminal); write('steady-state.json', gate); write('summary.json', summary);
checkpoint.phase = 'complete'; checkpoint.gateSuccess = gate.success; checkpoint.completedAtUTC = summary.completedAtUTC; saveCheckpoint();
console.log(`COMPLETE ${JSON.stringify(serial({contract: GT, policyCharacters: 100, transactions: journal.length,
  gate, counts, reserveUSDC: formatUnits(terminal.reserve, 6), stakeUSDC: formatUnits(terminal.stake, 6)}))}`);
