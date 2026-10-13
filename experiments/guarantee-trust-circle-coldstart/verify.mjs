/** Independent public-evidence verifier. Never reads a private key or sends a transaction. */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {AbiCoder, Contract, Interface, JsonRpcProvider, TypedDataEncoder, getAddress,
  hexlify, keccak256, toBeHex, toUtf8Bytes, zeroPadBytes, zeroPadValue} from 'ethers';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const OFFLINE = process.argv.includes('--offline');
const ai = process.argv.indexOf('--evidence');
const DIR = path.resolve(ai >= 0 ? process.argv[ai + 1] : process.env.COLDSTART_OUT || path.join(HERE, 'coldstart-evidence'));
const RPC = process.env.RPC_URL || process.env.COLDSTART_RPC || 'https://sepolia.base.org';
const SOURCE = 'ec93c76779b5e2d52ab7b87cf82b3fd400205969';
const read = n => JSON.parse(fs.readFileSync(path.join(DIR, n), 'utf8'));
const jlines = n => fs.readFileSync(path.join(DIR, n), 'utf8').split('\n').filter(Boolean).map(JSON.parse);
const serial = x => JSON.parse(JSON.stringify(x, (_, v) => typeof v === 'bigint' ? v.toString() : v));
const norm = x => typeof x === 'string' && /^0x[0-9a-f]+$/i.test(x) ? x.toLowerCase() : ['bigint','number'].includes(typeof x) ? x.toString() : x;
const equal = (x, y, label) => {if (norm(x) !== norm(y)) throw Error(`${label} mismatch`);};
const must = (x, label) => {if (!x) throw Error(label);};
const bi = x => BigInt(x);
const artifactBytes = fs.readFileSync(process.env.COLDSTART_ARTIFACT || path.join(HERE, 'artifact.json'));
const artifact = JSON.parse(artifactBytes);
const artifactSha = createHash('sha256').update(artifactBytes).digest('hex');
const gtInterface = new Interface(artifact.abi);
const tokenInterface = new Interface([
  'function transfer(address to,uint256 amount) returns(bool)',
  'function approve(address spender,uint256 amount) returns(bool)',
  'event Transfer(address indexed from,address indexed to,uint256 value)',
]);
const journal = read('transactions.json'), manifest = read('manifest.json'), summary = read('summary.json');
const deployment = read('deployment.json'), roundRows = read('rounds.json');
const authorGuarantees = read('guarantees.json'), policyEvents = jlines('policy-events.jsonl');
const priorDeployment = fs.existsSync(path.join(DIR,'prior-deployment.json')) ? read('prior-deployment.json') : null;
const GT = getAddress(deployment.contract), TOKEN = getAddress(deployment.token), ROOT = getAddress(manifest.rootAddress);
const result = {schema: 'guarantee-trust-independent-verification/1', startedAtUTC: new Date().toISOString(),
  mode: OFFLINE ? 'offline-not-chain-verification' : 'online-public-chain-verification',
  chainId: 84532, sourceCommit: SOURCE, contract: GT, token: TOKEN,
  proofLimitations: OFFLINE ? ['Uses published journal events; does not authenticate them against a blockchain.',
    'Token movement is inferred from pool accounting; no receipt or calldata proof.'] :
    ['Refusals and policy rounds are offchain records. Their counts are reconciled, not proved as onchain rejection events.',
      'Synthetic client payments do not prove external revenue, work or human benefit.'], success: false};
let provider;
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function retry(fn, label) {
  for (let attempt = 0; attempt < 6; attempt++) {
    try {return await fn();} catch (e) {
      if (attempt === 5) throw Error(`${label} unavailable after retries`);
      await sleep(Math.min(500 * 2 ** attempt, 8000));
    }
  }
}
function checkSource() {
  for (const x of [manifest, summary, deployment, artifact]) equal(x.sourceCommit, SOURCE, 'Reviewed source commit');
  equal(manifest.artifactSha256, artifactSha, 'Manifest artifact digest');
  equal(deployment.artifactSha256, artifactSha, 'Deployment artifact digest');
  for (const x of [manifest, summary, deployment]) equal(x.chainId, 84532, 'Evidence chain');
  equal(manifest.token, TOKEN, 'Manifest token'); equal(summary.token, TOKEN, 'Summary token');
  equal(summary.contract, GT, 'Summary contract');
  equal(manifest.policySeed, 20261013, 'Policy seed'); equal(summary.policySeed, 20261013, 'Summary seed');
  equal(manifest.rounds, 24, 'Manifest rounds'); equal(summary.rounds, 24, 'Summary rounds');
  const wanted = {clients: 40, workers: 40, backers: 14, sponsors: 4, issuer: 1, adjudicator: 1};
  for (const [k, v] of Object.entries(wanted)) {equal(manifest.roles[k], v, `Manifest ${k}`); equal(summary.roles[k], v, `Summary ${k}`);}
  equal(manifest.roster.length, 100, 'Policy character count');
  equal(new Set(manifest.roster.map(x => x.id)).size, 100, 'Unique policy identities');
  equal(new Set(manifest.roster.map(x => x.address.toLowerCase())).size, 99, 'Distinct EOA count');
  equal(summary.policyCharacters, 100, 'Summary policy characters'); equal(summary.independentAgents, 0, 'Independent agent count');
  equal(summary.humanEarnings, 0, 'Human earnings claim'); equal(summary.humanBenefit, 0, 'Human benefit claim');
  equal(roundRows.length, 24, 'Round snapshot count');
  roundRows.forEach((r, i) => equal(r.round, i + 1, 'Round sequence'));
  const hashes = new Set();
  let lastBlock = -1;
  for (const item of journal) {
    must(/^0x[0-9a-f]{64}$/i.test(item.hash), 'Malformed public transaction hash');
    must(!hashes.has(item.hash.toLowerCase()), 'Duplicate journal transaction'); hashes.add(item.hash.toLowerCase());
    equal(item.status, 1, `Published status ${item.label}`); equal(item.chainId, 84532, `Published chain ${item.label}`);
    must(item.blockNumber >= lastBlock, 'Journal block order'); lastBlock = item.blockNumber;
  }
  must(journal.length > 0, 'Empty transaction journal');
  const creations = journal.filter(x => x.call === 'constructor');
  if (creations.length) {
    equal(creations.length, 1, 'Creation transaction count');
    equal(creations[0].hash, deployment.deploymentHash, 'Deployment transaction link');
    must(!priorDeployment, 'Both current and prior deployment are recorded');
  } else {
    must(priorDeployment, 'Resumed execution lacks a prior deployment record');
    equal(priorDeployment.hash, deployment.deploymentHash, 'Prior deployment transaction link');
    equal(priorDeployment.contract, GT, 'Prior deployment target'); equal(priorDeployment.from, ROOT, 'Prior deployment operator');
    equal(priorDeployment.status, 1, 'Prior deployment published status');
    must(priorDeployment.blockNumber < journal[0].blockNumber, 'Prior creation must precede resumed execution');
    result.priorDeployment = {hash: priorDeployment.hash, blockNumber: priorDeployment.blockNumber,
      outsideCurrentExecutionBalanceWindow: true, authenticated: false, executionFeeWei: priorDeployment.feeWei};
  }
  result.roster = {policyCharacters: 100, distinctEOAs: 99, independentAgents: 0};
}

function compareAcceptance(actual, expected) {
  for (const f of gtInterface.getFunction('openGuarantee').inputs[0].components) equal(actual[f.name], expected[f.name], `Acceptance ${f.name}`);
}
function checkCalldata(item, tx) {
  equal(tx.hash, item.hash, `Transaction hash ${item.label}`);
  equal(tx.from, item.from, `Sender ${item.label}`); equal(tx.to, item.to, `Target ${item.label}`);
  equal(tx.nonce, item.nonce, `Nonce ${item.label}`); equal(Number(tx.chainId), 84532, `Transaction chain ${item.label}`);
  const a = item.args;
  if (item.call === 'native ETH transfer') {
    equal(tx.to, a.to, 'ETH recipient'); equal(tx.value, bi(a.value), 'ETH value'); equal(tx.data, '0x', 'ETH transfer data'); return;
  }
  if (item.call === 'constructor') {
    equal(tx.to, null, 'Creation target');
    const creation = typeof artifact.bytecode === 'string' ? artifact.bytecode : artifact.bytecode.object;
    must(tx.data.toLowerCase().startsWith(creation.toLowerCase()), 'Reviewed creation bytecode mismatch');
    const d = AbiCoder.defaultAbiCoder().decode(gtInterface.deploy.inputs, '0x' + tx.data.slice(creation.length));
    ['token', 'owner', 'adjudicator', 'issuer', 'issuerBudget', 'unit'].forEach((k, i) => equal(d[i], a[k], `Constructor ${k}`));
    return;
  }
  equal(tx.value, 0n, `Unexpected native value ${item.label}`);
  if (item.call.startsWith('USDC.')) {
    equal(tx.to, TOKEN, 'ERC20 contract');
    const p = tokenInterface.parseTransaction({data: tx.data, value: tx.value});
    equal(p.name, item.call.slice(5), 'ERC20 function');
    if (p.name === 'transfer') {equal(p.args[0], a.to || a.worker, 'Token recipient'); equal(p.args[1], a.amount ?? a.netWage, 'Token transfer amount');}
    else {equal(p.args[0], a.spender, 'Token spender'); equal(p.args[1], a.amount, 'Token approval amount');}
    return;
  }
  equal(tx.to, GT, `GuaranteeTrust target ${item.label}`);
  const p = gtInterface.parseTransaction({data: tx.data, value: tx.value});
  equal(p.name, item.call, `Function ${item.label}`);
  const layouts = {
    setParams: ['maxShareBps','floorMultiple','contributionBps','contributionCap','remitWindow','lineCap','attestCap','maxAttesters','maxOpenAttestees'],
    fundReserve: ['amount'], stake: ['amount'], attest: ['worker','amount'], setLine: ['worker','amount'],
    setConsentBySig: ['member','attester','allowed','nonce','deadline'], markPaid: ['id','wage','evidenceHash'],
    remit: ['id'], claim: ['id','evidenceHash'], openDispute: ['id','reasonHash'],
    cancelGuarantee: ['id','resolutionHash'], setPaused: ['paused'],
  };
  if (p.name === 'openGuarantee') compareAcceptance(p.args[0], a.acceptance);
  else {
    must(layouts[p.name], `Unsupported journal function ${p.name}`);
    layouts[p.name].forEach((k, i) => equal(p.args[i], a[k], `Calldata ${p.name}.${k}`));
  }
  // EIP-712 signatures are intentionally neither copied nor printed. The reviewed contract validates them.
}

async function acquire() {
  if (OFFLINE) return journal.map(item => ({item, events: item.events || [], transfers: [], receipt: null}));
  provider = new JsonRpcProvider(RPC, undefined, {cacheTimeout: 0, batchMaxCount: 1});
  equal(Number((await retry(() => provider.getNetwork(), 'RPC network')).chainId), 84532, 'RPC chain');
  if (manifest.rehearsal) must(['localhost','127.0.0.1','[::1]'].includes(new URL(RPC).hostname), 'Rehearsal proof requires localhost');
  else equal(TOKEN, getAddress('0x036CbD53842c5426634e7929541eC2318f3dCF7e'), 'Canonical Circle test USDC');
  if (priorDeployment) {
    const [receipt, tx] = await retry(async () => {
      const values = await Promise.all([provider.getTransactionReceipt(priorDeployment.hash), provider.getTransaction(priorDeployment.hash)]);
      must(values.every(Boolean), 'Prior transaction/receipt missing'); return values;
    }, 'Prior deployment');
    equal(receipt.status,1,'Prior creation receipt status'); equal(receipt.contractAddress,GT,'Prior creation contract');
    equal(receipt.from,ROOT,'Prior creation sender'); equal(receipt.to,null,'Prior creation receipt target');
    equal(receipt.blockNumber,priorDeployment.blockNumber,'Prior creation block'); equal(tx.blockNumber,receipt.blockNumber,'Prior creation transaction block');
    equal(receipt.gasUsed,priorDeployment.gasUsed,'Prior creation gas'); equal(receipt.fee,priorDeployment.feeWei,'Prior creation fee');
    checkCalldata({label:'prior-constructor',call:'constructor',hash:priorDeployment.hash,from:ROOT,to:null,nonce:tx.nonce,
      args:{token:TOKEN,owner:ROOT,adjudicator:ROOT,issuer:ROOT,issuerBudget:'6000000',unit:'1000000'}},tx);
    result.priorDeployment.authenticated = true;
    result.priorDeployment.constructorCalldataChecked = true;
  }
  const records = new Array(journal.length); let next = 0, finished = 0;
  async function worker() {
    while (next < journal.length) {
      const index = next++, item = journal[index];
      const [receipt, tx] = await retry(async () => {
        const values = await Promise.all([provider.getTransactionReceipt(item.hash), provider.getTransaction(item.hash)]);
        must(values.every(Boolean), 'Transaction/receipt missing'); return values;
      }, `Public transaction ${index + 1}`);
      equal(receipt.status, 1, `Receipt status ${item.label}`); equal(receipt.hash, item.hash, 'Receipt hash');
      equal(receipt.from, item.from, 'Receipt sender'); equal(receipt.to, item.to, 'Receipt target');
      equal(receipt.blockNumber, item.blockNumber, 'Receipt block'); equal(tx.blockNumber, item.blockNumber, 'Transaction block');
      checkCalldata(item, tx);
      if (item.call === 'constructor') equal(receipt.contractAddress, GT, 'Created contract address');
      const events = [], transfers = [];
      for (const log of receipt.logs) {
        if (norm(log.address) === norm(GT)) {
          const e = gtInterface.parseLog(log); must(e, 'Unrecognized GuaranteeTrust log');
          events.push({name: e.name, args: serial(e.args.toObject())});
        } else if (norm(log.address) === norm(TOKEN)) {
          try {const e = tokenInterface.parseLog(log); if (e?.name === 'Transfer') transfers.push(serial(e.args.toObject()));} catch {}
        }
      }
      equal(JSON.stringify(serial(events)), JSON.stringify(item.events || []), `Published GT event list ${item.label}`);
      records[index] = {item, events, transfers, receipt};
      finished++; if (finished % 25 === 0 || finished === journal.length) console.log(`VERIFY_RECEIPTS ${finished}/${journal.length}`);
    }
  }
  await Promise.all(Array.from({length: 4}, worker)); return records;
}

function replay(records) {
  const state = {reserve: 0n, stake: 0n, dues: 0n, sponsorCapital: 0n, outstanding: 0n, tokenBalance: 0n};
  const gs = new Map(), history = [], roundStats = Array.from({length: 24}, (_, i) =>
    ({round: i + 1, opened: 0, paid: 0, claimed: 0, cancelled: 0, wages: 0n, contributions: 0n, claims: 0n, sponsorTopups: 0n, reserveRefusals: 0}));
  let paused = false, executionFees = 0n, rootFees = 0n, gasFunded = 0n, wages = 0n, netWages = 0n, duesPaid = 0n, sponsorSeed = 0n, initialStake = 0n, laterStake = 0n, clientPrefunding = 0n;
  const clients = new Set(manifest.roster.filter(x => x.role === 'client').map(x => norm(x.address)));
  const refuseCounts = {};
  const policyOpen = new Map();
  for (const e of policyEvents) {
    must(e.round >= 1 && e.round <= 24, 'Policy event round');
    if (e.kind === 'refused') {
      refuseCounts[e.reason] = (refuseCounts[e.reason] || 0) + 1;
      if (['ExposureCap','GroupCap','ReserveFloor'].includes(e.reason)) roundStats[e.round - 1].reserveRefusals++;
    } else if (e.kind === 'opened') {
      must(!policyOpen.has(String(e.id)), 'Duplicate policy opening'); policyOpen.set(String(e.id), e);
    } else throw Error('Unknown policy event kind');
  }
  for (const {item, events, transfers, receipt} of records) {
    if (receipt) {
      executionFees += receipt.fee; if (norm(receipt.from) === norm(ROOT)) rootFees += receipt.fee;
      equal(receipt.gasUsed, item.gasUsed, 'Published gas used'); equal(receipt.fee, item.feeWei, 'Published execution fee');
    }
    if (item.call === 'native ETH transfer') gasFunded += bi(item.args.value);
    if (!OFFLINE && item.call === 'USDC.transfer') {
      equal(transfers.filter(t => norm(t.from) === norm(item.from) && norm(t.to) === norm(item.args.to || item.args.worker))
        .reduce((n,t) => n + bi(t.value),0n), bi(item.args.amount ?? item.args.netWage), 'Actual ERC20 transfer amount');
    }
    if (item.call === 'USDC.transfer' && /^tokens-client-/.test(item.label)) clientPrefunding += bi(item.args.amount);
    const wageMatch = /^wage-g(\d+)-/.exec(item.label);
    if (wageMatch) {
      const g = gs.get(wageMatch[1]); must(g && g.state === 1, 'Wage must follow an open guarantee');
      must(clients.has(norm(item.from)), 'Wage sender is not a roster client'); equal(item.args.worker, g.worker, 'Wage worker');
      equal(item.args.grossWage, bi(item.args.netWage) + bi(item.args.withheldContribution), 'Gross wage cash reconciliation');
      const actual = OFFLINE ? bi(item.args.netWage) : transfers.filter(t => norm(t.from) === norm(item.from) && norm(t.to) === norm(g.worker)).reduce((n, t) => n + bi(t.value), 0n);
      equal(actual, bi(item.args.netWage), 'Actual client-to-worker transfer');
      must(g.netWage === undefined, 'Duplicate wage payment'); g.netWage = actual; g.clientPayer = item.from;
    }
    for (const event of events) {
      const a = event.args, amount = a.amount === undefined ? null : bi(a.amount);
      switch (event.name) {
        case 'ReserveFunded': {
          state.reserve += amount; state.sponsorCapital += amount;
          equal(a.reserve, state.reserve, 'ReserveFunded reserve');
          if (/^seed-/.test(item.label)) sponsorSeed += amount;
          else {const m = /^topup-round-(\d+)-/.exec(item.label); must(m, 'Unexpected reserve injection'); must(Number(m[1]) <= 12, 'Late sponsor funding'); roundStats[Number(m[1]) - 1].sponsorTopups += amount;}
          break;
        }
        case 'ReserveReleased': state.reserve -= amount; state.sponsorCapital -= amount; break;
        case 'Staked': {
          state.stake += amount;
          if (/^stake-initial-/.test(item.label)) initialStake += amount;
          else {const m = /^stake-round-(\d+)-/.exec(item.label); must(m && Number(m[1]) <= 12, 'Late or unexplained stake'); laterStake += amount;}
          break;
        }
        case 'Unstaked': state.stake -= amount; break;
        case 'GuaranteeOpened': {
          const id = String(a.id), p = policyOpen.get(id), m = /^open-round-(\d+)-g/.exec(item.label);
          must(!gs.has(id) && Number(id) === gs.size, 'Guarantee IDs must be new and sequential');
          must(p && m, 'Opening lacks policy round'); equal(Number(m[1]), p.round, 'Opening round');
          equal(a.worker, p.acceptance.worker, 'Opened worker'); equal(a.amount, p.acceptance.amount, 'Opened amount');
          equal(a.clientId,p.acceptance.clientId,'Opened client identity'); equal(a.groupId,p.acceptance.groupId,'Opened client group');
          const policyClient = manifest.roster.find(x => x.id === p.terms.client);
          const policyWorker = manifest.roster.find(x => x.id === p.terms.worker);
          must(policyClient?.role === 'client' && policyWorker?.role === 'worker','Terms roster role identities');
          equal(policyClient.clientId,a.clientId,'Terms client ID'); equal(policyClient.groupId,a.groupId,'Terms client group');
          equal(policyWorker.address,a.worker,'Terms worker address');
          equal(a.termsHash, p.acceptance.termsHash, 'Opened terms hash');
          equal(keccak256(toUtf8Bytes(JSON.stringify(p.terms))), a.termsHash, 'Terms content hash');
          const g = {id, worker: a.worker, clientId: a.clientId, groupId: a.groupId, amount,
            fromBacking: bi(a.fromBacking), fromLine: bi(a.fromLine), fromDues: bi(a.fromDues), state: 1, round: p.round,
            expectedClientPayer: policyClient.address, remitted: false};
          equal(g.fromBacking + g.fromLine + g.fromDues, amount, 'Committed trust decomposition');
          gs.set(id, g); state.outstanding += amount; roundStats[p.round - 1].opened++; break;
        }
        case 'GuaranteePaid': {
          const g = gs.get(String(a.id)); must(g?.state === 1, 'Payment must settle an open guarantee');
          must(g.netWage !== undefined, 'Paid guarantee lacks a client-to-worker transfer');
          equal(g.clientPayer,g.expectedClientPayer,'Signed client paid the synthetic wage');
          g.state = 2; g.wage = bi(a.wage); g.contributionDue = bi(a.contributionDue);
          equal(g.netWage + g.contributionDue, g.wage, 'Paid gross wage reconciliation');
          equal(g.contributionDue, g.wage * 500n / 10000n > 300000n ? 300000n : g.wage * 500n / 10000n, 'Contribution policy');
          state.outstanding -= g.amount; roundStats[g.round - 1].paid++; roundStats[g.round - 1].wages += g.wage;
          wages += g.wage; netWages += g.netWage; break;
        }
        case 'GuaranteeCancelled': case 'GuaranteeExpired': {
          const g = gs.get(String(a.id)); must(g?.state === 1, 'Cancellation/expiry must settle an open guarantee');
          g.state = event.name === 'GuaranteeCancelled' ? 4 : 5; state.outstanding -= g.amount;
          if (g.state === 4) roundStats[g.round - 1].cancelled++; break;
        }
        case 'Claimed': {
          const g = gs.get(String(a.id)); must(g?.state === 1, 'Claim must settle an open guarantee'); equal(g.amount, amount, 'Claim amount');
          equal(g.worker, a.worker, 'Claim worker'); g.state = 3; state.outstanding -= amount; state.reserve -= amount;
          roundStats[g.round - 1].claimed++; roundStats[g.round - 1].claims += amount;
          if (!OFFLINE) equal(transfers.filter(t => norm(t.from) === norm(GT) && norm(t.to) === norm(g.worker)).reduce((n,t) => n + bi(t.value), 0n), amount, 'Actual claim payment');
          break;
        }
        case 'ContributionRemitted': {
          const g = gs.get(String(a.id)); must(g?.state === 2 && !g.remitted, 'Remittance must follow one unpaid contribution');
          equal(a.worker, g.worker, 'Remittance worker'); equal(a.payer, g.clientPayer, 'Withholding remitter'); equal(amount, g.contributionDue, 'Remittance amount');
          if (!OFFLINE) equal(transfers.filter(t => norm(t.from) === norm(a.payer) && norm(t.to) === norm(GT)).reduce((n,t) => n + bi(t.value), 0n), amount, 'Actual contribution transfer');
          g.remitted = true; state.reserve += amount; state.dues += amount; duesPaid += amount;
          roundStats[g.round - 1].contributions += amount; break;
        }
        case 'LineConsumed': state.sponsorCapital -= amount; break;
        case 'DuesConsumed': state.dues -= amount; break;
        case 'BackingConsumed': {
          const slash = bi(a.stakeSlashed); must(slash >= 0n && slash <= amount, 'Invalid backing slash');
          state.reserve += slash; state.stake -= slash; state.dues -= amount - slash; break;
        }
        case 'Paused': paused = a.paused; break;
        default: break;
      }
    }
    if (OFFLINE) state.tokenBalance = state.reserve + state.stake;
    else for (const t of transfers) {
      if (norm(t.to) === norm(GT)) state.tokenBalance += bi(t.value);
      if (norm(t.from) === norm(GT)) state.tokenBalance -= bi(t.value);
    }
    for (const [k, v] of Object.entries(state)) must(v >= 0n, `Negative event ledger ${k}`);
    equal(state.tokenBalance, state.reserve + state.stake, `Token accounting after ${item.label}`);
    equal(state.reserve, state.sponsorCapital + state.dues, `Capital accounting after ${item.label}`);
    if (item.ledgerAfter) for (const k of ['reserve','stake','dues','sponsorCapital','tokenBalance']) equal(state[k], bi(item.ledgerAfter[k]), `Published ledger ${k} after ${item.label}`);
    history.push({blockNumber: item.blockNumber, state: {...state}});
  }
  const eventCounts = {opened: gs.size, paid: 0, claimed: 0, cancelled: 0, expired: 0, remitted: 0};
  for (const g of gs.values()) {
    must(g.state !== 1, 'Open guarantee at terminal state');
    if (g.state === 2) {eventCounts.paid++; must(g.remitted, 'Unremitted terminal contribution');}
    if (g.state === 3) eventCounts.claimed++; if (g.state === 4) eventCounts.cancelled++; if (g.state === 5) eventCounts.expired++;
    if (g.remitted) eventCounts.remitted++;
    const published = authorGuarantees.find(x => String(x.id) === g.id); must(published, 'Missing published guarantee');
    for (const k of ['worker','clientId','groupId','state','amount','fromBacking','fromLine','fromDues','remitted']) equal(g[k], published[k], `Published guarantee ${g.id}.${k}`);
  }
  equal(authorGuarantees.length, gs.size, 'Published guarantee count'); equal(policyOpen.size, gs.size, 'Policy opening count');
  for (const k of ['opened','paid','claimed','cancelled','remitted']) equal(eventCounts[k], summary.counts[k], `Summary count ${k}`);
  equal(wages, summary.counts.wages, 'Summary gross wages'); equal(netWages, summary.counts.netWages, 'Summary net wages');
  equal(duesPaid, summary.counts.contributions, 'Summary contributions'); equal(wages, netWages + duesPaid, 'Aggregate gross wage identity');
  equal(roundStats.reduce((n,r) => n + r.claims, 0n), summary.counts.claims, 'Summary claims');
  equal(laterStake, summary.counts.laterStake, 'Summary additional stake');
  for (const [reason, n] of Object.entries(refuseCounts)) equal(summary.counts.refusals[reason], n, `Published refusal count ${reason}`);
  equal(Object.keys(summary.counts.refusals).length, Object.keys(refuseCounts).length, 'Refusal reason categories');
  equal(policyEvents.length, summary.counts.posted, 'Posted policy requests');
  equal(sponsorSeed, 2000000n, 'Reserve seed'); equal(initialStake, 4200000n, 'Initial backing stake'); equal(clientPrefunding, 800000000n, 'Client prefunding');
  must(gasFunded <= 5000000000000000n, 'Role gas funding exceeded cap');
  const stateAt = blockNumber => {const h = history.filter(h => h.blockNumber <= blockNumber).at(-1); must(h, 'Snapshot predates deployment'); return h.state;};
  const initialEventState = stateAt(summary.initial.blockNumber);
  for (const k of Object.keys(state)) equal(initialEventState[k],summary.initial[k],`Initial event ledger ${k}`);
  let priorReserve = bi(summary.initial.reserve);
  for (let i = 0; i < 24; i++) {
    const r = roundRows[i], e = roundStats[i], s = stateAt(r.blockNumber);
    for (const k of Object.keys(state)) equal(s[k], r[k], `Round ${i + 1} event ledger ${k}`);
    equal(r.reserveBefore, priorReserve, `Round ${i + 1} reserve before`); priorReserve = s.reserve;
    for (const k of ['opened','paid','claimed','cancelled','wages','contributions','claims','sponsorTopups','reserveRefusals']) equal(e[k], r[k], `Round ${i + 1} ${k}`);
    must(r.identities?.tokenEqualsReservePlusStake && r.identities?.reserveEqualsSponsorCapitalPlusDues, 'Published round identity false');
  }
  const last = roundRows.slice(-6), stats = roundStats.slice(-6);
  const gate = {windowRounds: [19,24], sponsorTopups: stats.reduce((n,r) => n + r.sponsorTopups, 0n),
    opened: stats.reduce((n,r) => n + r.opened, 0), throughputEachRound: stats.every(r => r.opened > 0),
    reserveChange: bi(last.at(-1).reserve) - bi(last[0].reserveBefore),
    reserveRefusals: stats.reduce((n,r) => n + r.reserveRefusals, 0), identitiesAllRounds: true};
  gate.success = gate.sponsorTopups === 0n && gate.throughputEachRound && gate.reserveChange >= 0n && gate.reserveRefusals === 0;
  for (const k of ['sponsorTopups','opened','throughputEachRound','reserveChange','reserveRefusals','identitiesAllRounds','success']) equal(gate[k], summary.gate[k], `Summary gate ${k}`);
  equal(JSON.stringify(summary.gate.windowRounds), '[19,24]', 'Gate window');
  equal(roundStats.reduce((n,r) => n + r.sponsorTopups, 0n), summary.sponsorTopups, 'Summary sponsor topups');
  for (const k of Object.keys(state)) equal(state[k], summary.terminal[k], `Terminal summary ${k}`);
  equal(state.outstanding, 0n, 'Terminal exposure'); must(paused, 'Origination is not paused');
  return {state, gs, eventCounts, gate, paused, executionFees, rootFees, gasFunded, wages, netWages, duesPaid, sponsorSeed, initialStake, laterStake, clientPrefunding};
}

async function checkLive(replayed) {
  const gt = new Contract(GT, artifact.abi, provider);
  const token = new Contract(TOKEN, ['function balanceOf(address) view returns(uint256)'], provider);
  const finalBlock = summary.terminal.blockNumber;
  must(finalBlock >= journal.at(-1).blockNumber, 'Terminal block predates shutdown transaction');
  for (const tag of [finalBlock, 'latest']) {
    const o = {blockTag: tag};
    const values = await retry(() => Promise.all([gt.reserve(o), gt.totalStake(o), gt.totalDues(o), gt.sponsorCapital(o),
      gt.outstanding(o), token.balanceOf(GT, o), gt.guaranteeCount(o), gt.paused(o), gt.token(o), gt.owner(o), gt.issuer(o), gt.adjudicator(o)]), `Terminal views ${tag}`);
    const keys = ['reserve','stake','dues','sponsorCapital','outstanding','tokenBalance'];
    keys.forEach((k,i) => equal(values[i], replayed.state[k], `Live ${tag} ${k}`));
    equal(values[6], BigInt(replayed.gs.size), `Live ${tag} guarantee count`); equal(values[7], true, `Live ${tag} paused`);
    equal(values[8], TOKEN, 'Live token binding'); for (const v of values.slice(9)) equal(v, ROOT, 'Live operator role binding');
  }
  let next = 0; const all = [...replayed.gs.values()];
  async function worker() {
    while (next < all.length) {
      const g = all[next++];
      const live = await retry(() => gt.guarantee(g.id, {blockTag: finalBlock}), `Terminal guarantee ${g.id}`);
      for (const k of ['worker','clientId','groupId','state','amount','fromBacking','fromLine','fromDues','remitted']) equal(live[k], g[k], `Live guarantee ${g.id}.${k}`);
    }
  }
  await Promise.all(Array.from({length: 4}, worker));
  const code = await retry(() => provider.getCode(GT, finalBlock), 'Deployed runtime');
  const runtime = typeof artifact.deployedBytecode === 'string' ? artifact.deployedBytecode : artifact.deployedBytecode.object;
  equal(code.length, runtime.length, 'Runtime length');
  const refs = artifact.immutableReferences || artifact.deployedBytecode.immutableReferences;
  const domain = {name: 'GuaranteeTrust', version: '2', chainId: 84532, verifyingContract: GT};
  const want = {'56710': zeroPadValue(TOKEN,32), '1424': zeroPadValue(toBeHex(84532),32), '1426': zeroPadValue(GT,32),
    '1428': keccak256(toUtf8Bytes('GuaranteeTrust')), '1430': keccak256(toUtf8Bytes('2')), '1422': TypedDataEncoder.hashDomain(domain),
    '1433': toBeHex(BigInt(zeroPadBytes(hexlify(toUtf8Bytes('GuaranteeTrust')),32)) | 14n,32),
    '1436': toBeHex(BigInt(zeroPadBytes(hexlify(toUtf8Bytes('2')),32)) | 1n,32)};
  equal(Object.keys(refs).sort().join(','), Object.keys(want).sort().join(','), 'Immutable identifier set');
  const actualBytes = Buffer.from(code.slice(2),'hex'), expectedBytes = Buffer.from(runtime.slice(2),'hex');
  const occupied = new Set();
  for (const [id, expected] of Object.entries(want)) {
    must(refs[id]?.length, 'Missing immutable references'); if (id === '56710') equal(refs[id].length,7,'Token immutable occurrences');
    for (const {start,length} of refs[id]) {
      equal(length,32,'Immutable word length'); must(start >= 0 && start + length <= actualBytes.length, 'Immutable offset bounds');
      equal('0x'+actualBytes.subarray(start,start+length).toString('hex'), expected, `Runtime immutable ${id}`);
      for (let i = start; i < start + length; i++) {must(!occupied.has(i),'Overlapping immutable spans'); occupied.add(i);}
      actualBytes.fill(0,start,start+length); expectedBytes.fill(0,start,start+length);
    }
  }
  must(actualBytes.equals(expectedBytes), 'Reviewed runtime mismatch outside immutable words');
  equal(keccak256(code), deployment.runtimeHash, 'Published runtime hash');
  equal(keccak256('0x'+actualBytes.toString('hex')), deployment.maskedRuntimeHash, 'Published masked runtime hash');
  result.runtime = {bytes: actualBytes.length, immutableWords: occupied.size / 32, allImmutableValuesVerified: true,
    runtimeHash: keccak256(code), reviewedCodeOutsideImmutablesMatches: true};
  result.liveViews = {finalRecordedBlock: finalBlock, latestAlsoMatches: true, guaranteesChecked: all.length};
}

try {
  checkSource(); console.log(`VERIFY_START ${result.mode} ${journal.length} transactions`);
  const records = await acquire(); const replayed = replay(records);
  if (!OFFLINE) await checkLive(replayed);
  result.success = true; result.completedAtUTC = new Date().toISOString();
  result.transactions = {count: journal.length, receiptsAuthenticated: !OFFLINE, calldataChecked: !OFFLINE,
    everyPublishedLedgerReconciles: true, tokenTransfersIndependentlyReplayed: !OFFLINE};
  result.counts = replayed.eventCounts; result.terminal = replayed.state; result.gate = replayed.gate;
  result.payments = {grossWages: replayed.wages, actualNetWages: replayed.netWages,
    withheldContributions: replayed.duesPaid, grossEqualsNetPlusContributions: true,
    physicalTransfersAuthenticated: !OFFLINE};
  result.funding = {sponsorSeed: replayed.sponsorSeed, initialBackerStake: replayed.initialStake,
    additionalStake: replayed.laterStake, clientPrefunding: replayed.clientPrefunding, roleGasFundedWei: replayed.gasFunded};
  if (!OFFLINE) result.fees = {executionFeeWei: replayed.executionFees, rootExecutionFeeWei: replayed.rootFees,
    priorDeploymentExecutionFeeWei: priorDeployment ? bi(priorDeployment.feeWei) : 0n,
    executionFeeIncludingPriorDeploymentWei: replayed.executionFees + (priorDeployment ? bi(priorDeployment.feeWei) : 0n),
    includesBaseL1DataFees: false};
  fs.writeFileSync(path.join(DIR,'verification.json'), JSON.stringify(serial(result),null,2)+'\n');
  console.log(`VERIFY_COMPLETE ${JSON.stringify(serial({mode: result.mode, success: true, transactions: journal.length, counts: result.counts, gate: result.gate}))}`);
} catch (e) {
  result.completedAtUTC = new Date().toISOString();
  result.failure = String(e.message || 'Verification failed').replace(/https?:\/\/\S+/g,'[RPC]')
    .replace(/0x[0-9a-fA-F]{66,}/g,'[redacted payload]').slice(0,500);
  fs.writeFileSync(path.join(DIR,'verification.json'), JSON.stringify(serial(result),null,2)+'\n');
  console.error(`VERIFY_FAILED ${result.failure}`); process.exitCode = 1;
} finally {if (provider) provider.destroy();}
